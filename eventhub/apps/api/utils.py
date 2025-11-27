from django.db.models import (Case, ExpressionWrapper, F, FloatField, Min, Q,
                              Sum, Value, When)
from django.utils import timezone
from events.models import Event


def filter_events(request_query, hide_sold_out=True, event_annotation=True):
    """
    Get upcoming events with optional search term.

    Filters:
        Basic Filters:
        - Events must be upcoming (date >= now).
        - Event organizer has setup Stripe payouts to receive payments from ticket purchases.
        
        Optional Filters:
        - Sold-out events are excluded (optional).
        
        Search Query Filters:
        - Event must match the query against name, location or category (case-insensitive).
    
    Annotations:
        - total_seats, sold_seats
        - lowest_price
        - percent_sold
        - badge ('Hot' if >80% sold)
        - badge ('Sold Out' if all seats are sold)

    Returns:
        QuerySet of Event objects, optionally filtered and annotated.
    """

    # basic event filters
    events = Event.objects.filter(
        date__gte=timezone.now(),
        organizer__stripe_account__stripe_account_ready=True
    ).annotate(
        event_seats=Sum('price_zones__seats'),
        event_seats_sold=Sum('price_zones__seats_sold')
    )

    # optional sold-out filter
    if hide_sold_out:
        events = events.filter(event_seats_sold__lt=F('event_seats'))

    # optional event annotations
    if event_annotation:
        events = events.annotate(
            lowest_price=ExpressionWrapper(
                Min('price_zones__price'),
                output_field=FloatField()
            ),
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

    # search query filter
    search_query = request_query.get('q', '').strip()
    if search_query:
        events = events.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    return events.distinct()
