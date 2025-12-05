from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.db import transaction
from events.models import EventPriceZone
from tickets.models import Ticket, TicketInProcess

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

def calculate_order_totals(tickets):
    """
    Accumulate the price summary for tickets.

    Args:
        tickets (TicketInProcess QuerySet): Tickets and their price zone information.

    Returns:
        tuple: (subtotal, service_fee, tax, total)
    """

    subtotal = Decimal(0)
    for ticket in tickets:
        subtotal += ticket.price_zone.price

    subtotal = _round(subtotal)
    service_fee = _round( subtotal * Decimal(SERVICE_FEE) )
    tax = _round( subtotal * Decimal(TAX) )
    total = _round( subtotal + service_fee + tax )
    return subtotal, service_fee, tax, total

def reserve_tickets(tickets, reserver):
    """
    Save tickets in process (reserved tickets) to db.

    Args:
        tickets (list of dictionaries): Ticket selection data.
        reserver (Profile): The user for whom tickets are being reserved.

    Returns:
        QuerySet: A queryset of the created TicketInProcess objects with reserver and price zone associated with each.
    """

    created_tickets_ids = []

    for t in tickets:
        price_zone = EventPriceZone.objects.filter(id=t.get("id")).first()
        if price_zone:
            for _ in range(t.get('quantity')):
                ticket = TicketInProcess.objects.create(reserver = reserver, price_zone = price_zone)
                created_tickets_ids.append(ticket.id)

    return TicketInProcess.objects.filter(id__in=created_tickets_ids)

def save_tickets(tickets, order):
    """
    Save tickets (Ticket) to db and associate them with successful order.
    
    Function uses transaction.atomic for data consistency.
    Either both operations (Ticket creation and TicketInProcess deletion) succeed and database is updated for both
        or if any fails, the function doesn't update database for neither. 

    Args:
        tickets (TicketInProcess QuerySet): Tickets for which payment was confirmed.
        order (Order): Order to which tickets belong to.
    """

    with transaction.atomic():
        # create Ticket objects
        for ticket in tickets:
            Ticket.objects.create(price_zone=ticket.price_zone, order=order)

        # delete TicketInProcess objects
        tickets.delete()
