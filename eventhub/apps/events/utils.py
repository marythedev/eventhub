from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from tickets.models import Ticket

from .models import EventPriceZone

SERVICE_FEE = settings.SERVICE_FEE
TAX = settings.TAX

def _round(number):
    """
    Round decimal number up if it is more than 0.5.

    Args:
        number (float or Decimal): Input number to round.

    Returns:
        Decimal: Rounded number to 2 decimal places.
    """

    return Decimal(number).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_order_totals(selected_tickets):
    """
    Accumulate the price summary for selected tickets.

    Args:
        selected_tickets: List of dictionaries of selected tickets.
            Each ticket has { id, quantity (selected quantity), total (price * quantity) }

    Returns:
        tuple: (subtotal, service_fee, tax, total)
    """

    subtotal = Decimal(0)
    for ticket in selected_tickets:
        subtotal += Decimal(ticket.get("total"))

    subtotal = _round(subtotal)
    service_fee = _round( subtotal * Decimal(SERVICE_FEE) )
    tax = _round( subtotal * Decimal(TAX) )
    total = _round( subtotal + service_fee + tax )
    return subtotal, service_fee, tax, total


def save_tickets(purchased_tickets, order):
    """
    Save tickets to db and associate them with successful order.
    Update ticket quantity for the event (tickets have been purchased).

    Args:
        purchased_tickets (list of dictionaries): Ticket selection data.
        order (Order): Order to which tickets belong to.
    """

    for t in purchased_tickets:
        price_zone = EventPriceZone.objects.filter(id=t.get("id")).first()
        if price_zone:
            for _ in range(t.get('quantity')):
                Ticket.objects.create(
                    price_zone = price_zone,
                    order = order
                )
