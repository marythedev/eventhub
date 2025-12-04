from core.utils.event_filter_utils import filter_events_custom
from core.utils.utils import get_unique_events_from_orders
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from events.models import Event, Order

from .models import Ticket
from .utils import validate_ticket


@login_required
def event_tickets(request, event_id):
    """
    Page that displays user's owned tickets for specific event.

    Behavior:
        - Ensures the event exists.
        - Retrieves only tickets that belong to the logged-in user.

    Args:
        request (HttpRequest)
        event_id (int): ID of the event for which user's tickets should be displayed.
    """

    event = get_object_or_404(Event, id=event_id)
    owned_tickets = Ticket.objects.filter(
        order__acquirer=request.user,
        price_zone__event=event
    )

    return render(request, 'tickets/event-tickets.html', { 'event': event, 'tickets_user_owns': owned_tickets })


@login_required
def validate_tickets(request, event_id):
    """
    Display the ticket validation page for an event.
    Only the event organizer or event team members are allowed to access.
    
    Raises:
        Http404: If event does not exist or user does not have permission to access.

    Args:
        request (HttpRequest)
        event_id (int): The ID of the event for which ticket validation page should be displayed.
    """

    event = get_object_or_404(Event, id=event_id)
    if not (event.organizer == request.user or event.is_team_member(request.user)):
        raise Http404("Event not found.")

    result = None
    if request.method == "POST":
        result = validate_ticket(
            ticket_number=request.POST.get("ticket_number"),
            event_id=request.POST.get("event_id"),
            user=request.user,
        )

    return render(request, "tickets/validate-tickets.html", {
        "event": event,
        "result": result
    })


@login_required
def view_orders(request):
    """
    Display a list of all orders made by the user.

    Events from orders are filtered based on request.GET search & filters query and ordered by date.
    Orders are filtered based on these events.
    """

    events = get_unique_events_from_orders(request.user)
    events = filter_events_custom(events, request.GET).order_by('date')

    # get orders for filtered events
    orders = request.user.orders.filter(
        tickets__price_zone__event__in=events
    ).distinct().order_by('-date')

    paginator = Paginator(orders, 3)
    page_number = request.GET.get('page')
    paginated_orders = paginator.get_page(page_number)

    # remove page parameter
    query = request.GET.copy()
    query.pop('page', None)

    return render(request, 'tickets/view-orders.html', {
        'paginated_orders': paginated_orders,
        'query': query
    })


@login_required
def order_tickets(request, order_id):
    """
    Page that displays user's owned tickets of the specific order.

    Behavior:
        - Validates that the order exists and is owned by the logged-in user.
        - Shows all tickets that were purchased in this order.

    Args:
        request (HttpRequest)
        order_id (int): ID of the order for which user's tickets should be displayed.
    """

    order = get_object_or_404(Order, id=order_id, acquirer=request.user)

    return render(request, 'tickets/order-tickets.html', { 'order': order })
