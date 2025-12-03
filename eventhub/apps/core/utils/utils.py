from django.db.models import (Case, Count, ExpressionWrapper, F, FloatField, Q,
                              Value, When)
from django.utils import timezone
from events.models import Event


def get_unique_events_from_orders(user):
    """
    Get all unique events to which user has purchased at least 1 ticket.
    Collects unique event IDs from the first ticket from each order. Filters events queryset based on those IDs.

    Args:
        user (Profile): The user whose orders are being retrieved.

    Returns:
        Filtered Event QuerySet.
    """

    orders = user.orders.all().prefetch_related("tickets__price_zone__event")

    event_ids = set()
    for order in orders:
        ticket = order.tickets.first()
        if ticket:
            event_ids.add(ticket.price_zone.event_id)

    return Event.objects.filter(id__in=event_ids)

def get_upcoming_user_events(user):
    """
    Get upcoming events that user has purchased tickets for.
    Annotates each event with the number of tickets the user owns for that event.

    Args:
        user (User): User whose upcoming events are being fetched.

    Returns:
        QuerySet: Upcoming events ordered by date with 'tickets_owned' annotation.
    """

    upcoming_events = get_unique_events_from_orders(user).filter(
        date__gte=timezone.now()
    )

    # owned ticket number annotation
    upcoming_events = upcoming_events.annotate(
        tickets_owned=Count(
            'price_zones__tickets',
            filter=Q(price_zones__tickets__order__acquirer=user)
        )
    ).order_by('date')

    return upcoming_events

def add_event_annotations(events):
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
