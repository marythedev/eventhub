import os
from datetime import datetime, time
from datetime import timezone as dt_timezone
from math import asin, cos, radians, sin, sqrt
from zoneinfo import ZoneInfo

import requests
from django.core.exceptions import ValidationError
from django.db.models import (Case, ExpressionWrapper, F, FloatField, Max, Min,
                              Q, Sum, Value, When)
from django.utils import timezone
from events.models import Event


def _event_basic_filter(events):
    """
    Apply basic event filters:
        - Events must be upcoming (date >= now).
        - Event organizer has setup Stripe payouts to receive payments from ticket purchases.

    Args:
        events: initial QuerySet of Event to filter

    Returns:
        Annotated filtered Event QuerySet with total seats, seats sold, lowest and highest prices.
        These are necessary annotations for further filtering (if applicable).
    """

    return (
        events.filter(
            date__gte=timezone.now(),
            organizer__stripe_account__stripe_account_ready=True
        )
        .annotate(
            event_seats=Sum("price_zones__seats"),
            event_seats_sold=Sum("price_zones__seats_sold"),
            lowest_price=ExpressionWrapper(Min("price_zones__price"), output_field=FloatField()),
            highest_price=ExpressionWrapper(Max("price_zones__price"), output_field=FloatField())
        )
        .distinct()
    )

def _event_search_filter(events, query):
    """
    Filter events by search query against name, location or category (case-insensitive).

    Args:
        events: initial QuerySet of Event to filter
        query: GET parameters

    Returns:
        Filtered Event QuerySet
    """

    search_query = query.get('search', '').strip()
    if search_query:
        events = events.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(category__icontains=search_query)
        ).distinct()
    return events

def _event_price_filters(events, query):
    """
    Filter events by price: min_price, max_price, free_only.
    In case free_only is selected, price range (min_price, max_price) is disregarded and removed from query.

    Args:
        events: initial QuerySet of Event to filter
        query: GET parameters

    Returns:
        Tuple: (filtered Event QuerySet, cleaned query dict)
    """

    min_price = query.get('min_price')
    max_price = query.get('max_price')
    free_only = query.get('free_only')

    if min_price:
        try:
            min_price = float(min_price)
            events = events.filter(highest_price__gte=min_price)
        except ValueError:
            pass

    if max_price:
        try:
            max_price = float(max_price)
            events = events.filter(lowest_price__lte=max_price)
        except ValueError:
            pass

    if free_only in ['true', '1', 'on']:
        events = events.filter(lowest_price=0)
        query.pop('min_price', None)
        query.pop('max_price', None)

    return events.distinct(), query

def _event_date_filters(events, query):
    """
    Filter events by date range using user timezone.

    Args:
        events: initial QuerySet of Event to filter
        query: GET parameters

    Returns:
        Filtered Event QuerySet
    """

    date_from = query.get('date_from')
    date_to = query.get('date_to')
    tz = query.get('timezone')

    user_tz = None
    try:
        user_tz = ZoneInfo(tz) if tz else None
    except Exception:      # pylint: disable=broad-exception-caught
        pass

    if date_from:

        # get local date start (time is midnight)
        local_start = datetime.combine(
            datetime.fromisoformat(date_from).date(),
            time.min
        ).replace(tzinfo=user_tz)

        # get utc date start & compare to event date (utc)
        utc_start = local_start.astimezone(dt_timezone.utc)
        events = events.filter(date__gte=utc_start)

    if date_to:
        # get local date end (time is the end of the day)
        local_end = datetime.combine(
            datetime.fromisoformat(date_to).date(),
            time.max
        ).replace(tzinfo=user_tz)

        # get utc date end & compare to event date (utc)
        utc_end = local_end.astimezone(dt_timezone.utc)
        events = events.filter(date__lte=utc_end)

    return events.distinct()

def _event_category_filter(events, query):
    """
    Filter events by selected categories.
    
    Args:
        events: initial QuerySet of Event to filter
        query: GET parameters

    Returns:
        Filtered Event QuerySet
    """

    selected_categories = query.getlist('category')
    if selected_categories:
        events = events.filter(category__in=selected_categories)
    return events.distinct()

def _add_event_annotations(events):
    """
    Add event annotations:
        - percent_sold
        - badge ('Hot' if >80% sold)
        - badge ('Sold Out' if all seats are sold)
    
    Args:
        events: initial QuerySet of Event to annotate

    Returns:
        Annotated Event QuerySet
    """

    return events.annotate(
        percent_sold=ExpressionWrapper(
            F('event_seats_sold') * 1.0 / F('event_seats'),
            output_field=FloatField()
        ),

        badge=Case(
            When(event_seats_sold__gte=F('event_seats'), then=Value('Sold Out')),
            When(percent_sold__gt=0.8, then=Value('Hot')),
            default=Value(''),
        )
    )

def _event_location_filter(events, query):
    """
    Filter events by location within a radius (in km).
    In case location is invalid, it is disregarded and removed from query.
    
    Args:
        events: initial QuerySet of Event to filter
        query: GET parameters

    Returns:
        Tuple: (filtered Event QuerySet, cleaned query dict)
    """

    location = query.get('location', '').strip()
    if location:
        try:
            location, lat, lon = validate_location(location)
            radius = float(query.get('radius', 25))

            if lat and lon:
                # generic fast location filter (square around the location)
                lat_diff = radius / 111
                lon_diff = radius / (111 * cos(radians(lat)))
                events = events.filter(
                    location_lat__gte=lat - lat_diff,
                    location_lat__lte=lat + lat_diff,
                    location_lon__gte=lon - lon_diff,
                    location_lon__lte=lon + lon_diff,
                )

                # additional precise location filter by haversine (circle around the location)
                filtered_ids = [
                    e.id for e in events
                    if _haversine(lat, lon, e.location_lat, e.location_lon) <= radius
                ]
                events = events.filter(id__in=filtered_ids)

        except ValidationError:
            query.pop('location', None)
            query.pop('radius', None)

    return events, query

def _haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of the first point.
        lat2, lon2: Latitude and longitude of the second point.

    Returns:
        Distance in kilometers
    """

    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * 6371 * asin(sqrt(a))


def validate_location(location):
    """
    Validate and normalize a location string using OpenStreetMap API.

    Behavior:
        - Fetch OpenStreetMap with the provided location string.
        - Ensure at least one result exists.
        - Normalize location input with the display_name returned by OpenStreetMap.

    Args:
        location (str): Location to be validated.

    Raises:
        ValidationError when:
            - Location is not valid (not found).
            - OpenStreetMap fetch fails.

    Returns:
        location (str): Validated and normalized location string.
    """

    try:
        # fetch openstreetmap to check if location exists
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': location, 'format': 'json'},
            headers={
                'User-Agent': f'Eventhub/{os.getenv("APP_VERSION", "1.0")}',
                'Accept-Language': 'en'
            },
            timeout=10
        )
        data = response.json()

        if len(data) == 0:
            raise ValidationError("Location not found. Please enter a valid place.")

        # transform location to full display name for consistent location format
        location = data[0]['display_name']
        latitude = float(data[0]['lat'])
        longitude = float(data[0]['lon'])

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("Failed to validate location. Try again later.") from e

    return location, latitude, longitude

def filter_events(request_query, hide_sold_out=True, event_annotation=True):
    """
    Apply all filters to events based on user query parameters.
    
    List of all filters:
        Basic filters.
        Sold out filter.
        Search query filter.
        Price filters.
        Date filters.
        Category filters.
        Location & location radius filter.

    Args:
        request_query: GET parameters
        hide_sold_out: bool, if True, exclude sold-out events
        event_annotation: bool, if True, add annotations

    Returns:
        Tuple: (filtered Event QuerySet, cleaned query dict)
    """

    # basic filters
    events = _event_basic_filter(Event.objects.all())

    if hide_sold_out:
        events = events.filter(event_seats_sold__lt=F('event_seats'))

    if event_annotation:
        events = _add_event_annotations(events)

    # query filters
    query = request_query.copy()
    events = _event_search_filter(events, query)
    events, query = _event_price_filters(events, query)
    events = _event_date_filters(events, query)
    events = _event_category_filter(events, query)
    events, query = _event_location_filter(events, query)

    return events, query
