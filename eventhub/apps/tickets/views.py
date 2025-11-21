from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from events.models import Order

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
        
    return render(request, 'tickets/view-tickets.html', { 'order': order })