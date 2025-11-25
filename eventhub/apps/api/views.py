import io
from barcode import Code128
from barcode.writer import ImageWriter

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.http import HttpResponse, Http404, JsonResponse

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from events.models import Order
from tickets.models import Ticket

from .stripe_utils import get_stripe_account_link, delete_stripe_account

@login_required
def ticket_barcode(request, ticket_id):
    """
    Generate a barcode image for a ticket.
    Checks that the ticket belongs to the logged-in user and returns a barcode image of the ticket number.

    Args:
        request: Django request object.
        ticket_id (int): ID of the ticket in the database.

    Returns:
        HttpResponse: image of the barcode.

    Raises:
        Http404: If the ticket does not exist or does not belong to the logged-in user.
    """

    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if (ticket.order.acquirer != request.user):
        raise Http404("Ticket not found")

    buffer = io.BytesIO()
    barcode = Code128(ticket.number, writer=ImageWriter())
    barcode.write(buffer)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required
def order_receipt(request, order_id):
    """
    Generate a PDF receipt for an order.

    Receipt includes event details, tickets purchased with quantity and price,
    and a payment summary with subtotal, service fee, tax, and total.

    Args:
        request: Django request object.
        order_id (int): ID of the order in the database.

    Returns:
        HttpResponse: order receipt PDF file.

    Raises:
        Http404: If the order does not exist or does not belong to the logged-in user.
    """

    order = get_object_or_404(Order, id=order_id, acquirer=request.user)

    tickets = (
        order.tickets
        .values("price_zone__name", "price_zone__price")
        .annotate(quantity=Count("id"))
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40,
                            title=f"Receipt for Order #{order.number}")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=20
    )
    header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        textColor="#333333",
        spaceBefore=15,
        spaceAfter=8
    )
    normal = styles["BodyText"]
    normal.spaceAfter = 6

    elements = []

    # Header
    elements.append(Paragraph("EVENTHUB RECEIPT", title_style))
    elements.append(Paragraph(f"Order #: <b>{order.number}</b>", normal))
    elements.append(Paragraph(f"Purchase Date: <b>{order.date.strftime('%Y-%m-%d %H:%M %Z')}</b>", normal))
    elements.append(Spacer(1, 20))

    # Event Info
    elements.append(Paragraph("Event Details", header_style))
    elements.append(Paragraph(f"Event Name: <b>{order.event.name}</b>", normal))
    elements.append(Paragraph(f"Location: {order.event.location}", normal))
    elements.append(Paragraph(f"Date: {order.event.date.strftime('%B %d, %Y at %I:%M %p %Z')}", normal))
    elements.append(Spacer(1, 12))

    # Tickets Table
    elements.append(Paragraph("Tickets Purchased", header_style))

    ticket_data = [["Ticket Type", "Quantity", "Total Price"]]
    for t in tickets:
        ticket_data.append([
            t['price_zone__name'],
            str(t['quantity']),
            f"${t['price_zone__price'] * t['quantity']:.2f}"
        ])

    ticket_table = Table(ticket_data, colWidths=[240, 80, 100])
    ticket_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), "#d3d3d3"),
        ("TEXTCOLOR", (0,0), (-1,0), "#000000"),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("ALIGN", (0,0), (0,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING", (0,0), (-1,0), 6),
        ("GRID", (0,0), (-1,-1), 0.5, "#888888")
    ]))

    elements.append(ticket_table)
    elements.append(Spacer(1, 20))


    # Totals Table
    elements.append(Paragraph("Payment Summary", header_style))

    totals_data = [
        ["Subtotal:", f"${order.subtotal:.2f}"],
        ["Service Fee:", f"${order.service_fee:.2f}"],
        ["Tax:", f"${order.tax:.2f}"],
        ["Total:", f"${order.total:.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[340, 80])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-2), "Helvetica"),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 25))

    # Footer
    footer = Paragraph(
        "Thank you for your purchase!<br/>This receipt serves as proof of payment.",
        ParagraphStyle("footer", fontSize=10, textColor="#555555", alignment=1)
    )
    elements.append(footer)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=receipt-{order.id}.pdf"

    return response


@login_required
def stripe_setup(request):
    """
    Retrieve Stripe onboarding or login link for the current user.

    Args:
        request: Django request object.

    Returns:
        JsonResponse (dictionary): 'account_id', 'onboarding_url' or 'login_link'.

    Raises:
        JsonResponse with status 500 if error encountered.
    """

    try:
        onboarding_url, login_url = get_stripe_account_link(request.user)

        return JsonResponse({
            'account_id': request.user.stripe_account.stripe_account_id,
            'onboarding_url': onboarding_url,
            'login_link': login_url
        })

    except Exception as e:
        print('Error with Stripe account: ', e)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def stripe_delete(request):
    """
    Delete the Stripe connected account of the current user.

    Args:
        request: Django request object.

    Returns:
        JsonResponse: {'success': True} if account has been deleted.

    Raises:
        JsonResponse with status 500 if error encountered.
    """

    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        if request.user.stripe_account.stripe_account_id:
            delete_stripe_account(request.user)
        return JsonResponse({'success': True})
    except Exception as e:
        print("Error deleting Stripe account:", e)
        return JsonResponse({'error': str(e)}, status=500)
