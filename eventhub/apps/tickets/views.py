from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from events.models import Event, Order
from .models import *

@login_required
def event_tickets(request, event_id):
    """
    The page where user can view tickets for specific event.
    """
    
    event = get_object_or_404(Event, id=event_id)
    owned_tickets = Ticket.objects.filter(
        order__acquirer=request.user,
        price_zone__event=event
    )
        
    return render(request, 'tickets/event-tickets.html', { 'event': event, 'tickets_user_owns': owned_tickets })

@login_required
def view_orders(request):
    """
    The page where user can view orders.
    """
    
    # TODO implement filtering, pagination & display only successfully paid orders (failed only for inner records in case of disputes)
    # TODO display time in local timezone (utc convert) + check other date displays
    all_orders = request.user.orders.all()
    
    return render(request, 'tickets/view-orders.html', { 'orders': all_orders })

@login_required
def order_tickets(request, order_id):
    """
    The page where user can view tickets for specific order.
    """
    
    order = get_object_or_404(Order, id=order_id, acquirer=request.user)
        
    return render(request, 'tickets/order-tickets.html', { 'order': order })
