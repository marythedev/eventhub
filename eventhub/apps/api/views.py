import io

from barcode import Code128
from barcode.writer import ImageWriter
from core.utils.event_filter_utils import (filter_events_custom,
                                           filter_events_global,
                                           get_filtered_paginated_events)
from core.utils.stripe_utils import (delete_stripe_account,
                                     get_stripe_account_link)
from core.utils.utils import get_unique_events_from_orders
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from events.models import Event, Order
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from tickets.models import Ticket

SUGGESTION_PREVIEW_NUM = 5

def load_events(request):
    """
    Get paginated list of events based on the search query and pagination page parameter.
    Filters events based on request GET parameters.
    Returns serialized list of events.
    """

    paginated_events, _ , _ = get_filtered_paginated_events(
        request, hide_sold_out=True, event_annotation=True
    )

    data = []
    for e in paginated_events:
        data.append({
            "id": e.id,
            "name": e.name,
            "date": e.date.isoformat(),
            "location": e.location,
            "category_label": e.category_label,
            "category_icon": e.category_icon,
            "min_price": e.min_price,
            "max_price": e.max_price,
            "badge": e.badge,
            "image_url": e.images.first().url
        })

    return JsonResponse({
        "events": data,
        "has_next": paginated_events.has_next()
    })


def search_all(request):
    """
    Return event suggestions for live search withing all events.
    Only allows requests with the header 'X-App-Request: true'.
    
    Displays events filtered by:
        - Basic filtering of 'filter_events_global' function (always).
        - Search query if given.
        - Includes sold-out events in the results.

    Events are not annotated with additional information by 'filter_events_global' for display.
    
    Args:
        request: Django HttpRequest with optional query parameter.

    Raises:
        Http404: if the request does not have 'X-App-Request' header set to 'true'.

    Returns:
        JSON list with SUGGESTION_PREVIEW_NUM events with basic info for displaying suggestions.
    """

    # prevent accidental direct access to search api via browser url
    if request.headers.get("X-App-Request") != "true":
        raise Http404()

    if not request.GET:
        return JsonResponse({"results": []})

    events, _ = filter_events_global(
        request.GET,
        hide_sold_out=False,
        event_annotation=False
    )
    events = events.order_by("date")[:SUGGESTION_PREVIEW_NUM]


    data = []
    for e in events:
        data.append({
            "id": e.id,
            "name": e.name,
            "location": e.location,
            "date": e.date,
            "image": e.images.first().url
        })

    return JsonResponse({"results": data})


@login_required
def search_my_events(request):
    """
    Return event suggestions for live search within the user's events.
    Only allows requests with the header 'X-App-Request: true'.

    Displays events filtered by:
        - Events that are created by the user.
        - Custom filtering of 'filter_events_custom' (names search + upcoming/past).

    Events are not annotated and display only basic information.

    Args:
        request: Django request object with optional query parameters.

    Raises:
        Http404: if the request does not have 'X-App-Request' header set to 'true'.

    Returns:
        JSON list with SUGGESTION_PREVIEW_NUM events with basic info for displaying suggestions.
    """

    # prevent accidental direct access to search api via browser url
    if request.headers.get("X-App-Request") != "true":
        raise Http404()

    if not request.GET:
        return JsonResponse({"results": []})

    events = filter_events_custom(request.user.events.all(), request.GET)
    events = events.order_by("date")[:SUGGESTION_PREVIEW_NUM]

    data = []
    for e in events:
        data.append({
            "id": e.id,
            "name": e.name,
            "location": e.location,
            "date": e.date,
            "image": e.images.first().url
        })

    return JsonResponse({"results": data})


@login_required
def search_events_from_orders(request):
    """
    Return event suggestions for live search within events the user has purchased tickets for.
    Only allows requests with the header 'X-App-Request: true'.

    Displays events filtered by:
        - Unique events connected to the user's orders.
        - Custom filtering by 'filter_events_custom' (name search + upcoming/past).

    Events are not annotated and display only basic information.

    Args:
        request: Django request object with optional query parameters.

    Raises:
        Http404: if the request does not have 'X-App-Request' header set to 'true'.

    Returns:
        JSON list with SUGGESTION_PREVIEW_NUM events with basic info for displaying suggestions.
    """

    # prevent accidental direct access to search api via browser url
    if request.headers.get("X-App-Request") != "true":
        raise Http404()

    if not request.GET:
        return JsonResponse({"results": []})

    events = get_unique_events_from_orders(request.user)
    events = filter_events_custom(events, request.GET)
    events = events.order_by("date")[:SUGGESTION_PREVIEW_NUM]

    data = []
    for e in events:
        data.append({
            "id": e.id,
            "name": e.name,
            "location": e.location,
            "date": e.date,
            "image": e.images.first().url
        })

    return JsonResponse({"results": data})


@login_required
def export_tickets(request, event_id):
    """
    Export all tickets issued for the event to CSV file.
    Only event organizer can export event tickets.

    The CSV has with ';' as the delimiter and the following columns:
        - Ticket Number
        - Ticket Owner Name
        - Ticket Owner Email
        - Purchase Date (formatted as 'DD MMM YYYY at HH:MM')
        - Order Associated with the Ticket

    Args:
        request: Django request object.
        event_id (int): ID of the event in the database for which ticket details are exported.

    Returns:
        HttpResponse: object with CSV content-type containing ticket information.
    """

    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.name}_tickets.csv"'

    csv_content = []
    header = [
        "Ticket Number", 
        "Ticket Owner Name", 
        "Ticket Owner Email", 
        "Purchase Date", 
        "Order Associated with the Ticket"
    ]
    csv_content.append(';'.join(header))

    ticket_data = [
        (
            f'"{str(ticket.number).strip()}"',
            f'"{str(ticket.order.acquirer.get_full_name()).strip()}"',
            f'"{str(ticket.order.acquirer.email).strip()}"',
            f'"{str(ticket.order.date.strftime('%d %b %Y at %H:%M')).strip()}"',
            f'"{str(ticket.order.number).strip()}"',
        )
        for price_zone in event.price_zones.all()
        for ticket in price_zone.tickets.all()
    ]

    def _get_email(ticket):
        """Return ticket owner's email."""
        return ticket[2]

    # sort tickets by ticket owner's email
    ticket_data.sort(key=_get_email)

    for ticket in ticket_data:
        csv_content.append(';'.join(ticket))

    response.content = "\n".join(csv_content)

    return response


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

    if ticket.order.acquirer != request.user:
        raise Http404("Ticket not found")

    buffer = io.BytesIO()
    barcode = Code128(ticket.number, writer=ImageWriter())
    barcode.write(buffer)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required
def order_receipt(request, order_id):       # pylint: disable=too-many-locals
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

    except Exception as e:      # pylint: disable=broad-exception-caught
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
    except Exception as e:      # pylint: disable=broad-exception-caught
        print("Error deleting Stripe account:", e)
        return JsonResponse({'error': str(e)}, status=500)
