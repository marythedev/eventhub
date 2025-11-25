from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from events.models import Event, Order

from .models import Ticket


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
def view_orders(request):
    """Display a list of all orders made by the user."""

    # TODO implement filtering, pagination & display only successfully paid orders
        # (failed only for inner records in case of disputes)
    all_orders = request.user.orders.all()

    return render(request, 'tickets/view-orders.html', { 'orders': all_orders })


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
