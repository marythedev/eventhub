from datetime import datetime, time
from datetime import timezone as dt_timezone
from math import cos, radians
from zoneinfo import ZoneInfo

from core.utils.utils import add_event_annotations
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import ExpressionWrapper, F, FloatField, Max, Min, Sum
from django.utils import timezone
from events.models import Event

from .event_search_utils import event_search_filter, event_search_name_filter
from .location_utils import haversine, validate_location


def event_basic_filter(events):
    """
    Apply basic event filters:
        - Events must be upcoming (date >= now).
        - Event organizer has setup Stripe payouts to receive payments from ticket purchases.

    Args:
        events: initial QuerySet of Event to filter

    Returns:
        Annotated filtered Event QuerySet with total seats, seats sold, reserved seats, lowest and highest prices.
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
            event_seats_reserved=Sum("price_zones__seats_reserved"),
            min_price=ExpressionWrapper(Min("price_zones__price"), output_field=FloatField()),
            max_price=ExpressionWrapper(Max("price_zones__price"), output_field=FloatField())
        )
        .distinct()
    )

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
            events = events.filter(max_price__gte=min_price)
        except ValueError:
            pass

    if max_price:
        try:
            max_price = float(max_price)
            events = events.filter(min_price__lte=max_price)
        except ValueError:
            pass

    if free_only in ['true', '1', 'on']:
        events = events.filter(min_price=0)
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
        Filtered Event QuerySet.
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
        Filtered Event QuerySet.
    """

    selected_categories = query.getlist('category')
    if selected_categories:
        events = events.filter(category__in=selected_categories)
    return events.distinct()

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
    if not location:
        query.pop('radius', None)
    else:
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
                    if haversine(lat, lon, e.location_lat, e.location_lon) <= radius
                ]
                events = events.filter(id__in=filtered_ids)

        except ValidationError:
            query.pop('location', None)
            query.pop('radius', None)

    return events, query

def filter_events_global(request_query, hide_sold_out=True, event_annotation=True):
    """
    Apply all filters to events based on user query parameters.
    
    List of all filters:
        Basic filters.
        Sold out filter.
        Name, location or category search.
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
    events = event_basic_filter(Event.objects.all())

    if hide_sold_out:
        events = events.filter(event_seats_sold__lt=F("event_seats") - F("event_seats_reserved"))

    if event_annotation:
        events = add_event_annotations(events)

    # query filters
    query = request_query.copy()
    events = event_search_filter(events, query)
    events, query = _event_price_filters(events, query)
    events = _event_date_filters(events, query)
    events = _event_category_filter(events, query)
    events, query = _event_location_filter(events, query)

    return events, query

def filter_events_custom(events, request_query):
    """
    Apply custom filters to a given Event queryset.
    
    List of all filters:
        Name search.
        Event date filter.
            - show="upcoming" - events occurring now or in the future
            - show="past"     - events that have already occurred
            - show="all"      - no date filtering (default)

    Args:
        events: initial QuerySet of Event to filter
        request_query: GET parameters

    Returns:
        Filtered Event QuerySet.
    """

    events = event_search_name_filter(events, request_query)

    show = request_query.get("show", "all")

    now = timezone.now()
    if show == "upcoming":
        events = events.filter(date__gte=now)

    elif show == "past":
        events = events.filter(date__lt=now)

    return events

def get_filtered_paginated_events(request, hide_sold_out=True, event_annotation=True):
    """
    Helper function to filter events based on query and apply pagination based on page.
    Displays 12 events per page (12 divisible by 2, 3, 4 - which will event card rows always even).
    
    Parameters:
    - request: Django HttpRequest with optional query parameters.
    - hide_sold_out: Whether to hide sold-out events.
    - event_annotation: Whether to annotate events with additional data for display.
    
    Returns:
    - paginated_events: Paginated list of filtered events.
    - request_query: The query filter parameters that were applied.
    - total_events: The total number of events that match query filters in the db.
    """

    search_query = request.GET.get('search')
    hide_sold_out = not search_query

    events, request_query = filter_events_global(
        request.GET,
        hide_sold_out=hide_sold_out,
        event_annotation=event_annotation
    )
    total_events = len(events)
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page', 1)
    paginated_events = paginator.get_page(page_number)

    return paginated_events, request_query, total_events
