import io
from barcode import Code128
from barcode.writer import ImageWriter

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from events.models import Ticket

def ticket_barcode(request, ticket_id):
    """Generate barcode for ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    buffer = io.BytesIO()
    barcode = Code128(ticket.number, writer=ImageWriter())
    barcode.write(buffer)

    return HttpResponse(buffer.getvalue(), content_type="image/png")