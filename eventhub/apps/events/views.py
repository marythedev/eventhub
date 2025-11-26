from datetime import datetime
from datetime import timezone as dt_timezone
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

import stripe
from api.stripe_utils import get_stripe_account
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import (Case, Count, ExpressionWrapper, F, FloatField,
                              Min, Sum, Value, When)
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tickets.models import Ticket
from users.utils import cloud_upload_img

from .forms import (EventImageValidator, EventInfoValidator,
                    OrderFormValidator, PriceZoneFormSet)
from .models import Event, EventImage, EventPriceZone, Order

# environmental variables
SERVICE_FEE = settings.SERVICE_FEE
TAX = settings.TAX
STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY


# helper functions
def _round(number):
    """
    Round decimal number up if it is more than 0.5.

    Args:
        number (float or Decimal): Input number to round.

    Returns:
        Decimal: Rounded number to 2 decimal places.
    """

    return Decimal(number).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def _calculate_order_totals(selected_tickets):
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

def _create_and_confirm_payment(total, payment_method_id, user_email):
    """
    Payment from customer to Eventhub via Stripe.
    Create and confirm a Stripe PaymentIntent.

    Args:
        total (Decimal): Charge amount in dollars.
        payment_method_id (str): ID of Stripe payment method from frontend Stripe fetch.
        user_email (str): Email of the customer for receipt.

    Returns:
        stripe.PaymentIntent: Confirmed PaymentIntent object.
    """

    stripe.api_key = STRIPE_SECRET_KEY
    payment_intent = stripe.PaymentIntent.create(
        amount=int(total * 100),
        currency="usd",
        payment_method=payment_method_id,
        receipt_email=user_email,
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"}
    )

    # payment confirmation
    confirmed_intent = stripe.PaymentIntent.confirm(
        payment_intent.id,
        payment_method=payment_method_id
    )
    return confirmed_intent

def _save_tickets(purchased_tickets, order):
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


# views
# TODO: filtering
def view_events(request):
    """
    Display events for users to explore.

    Displays events criteria:
        - event  is upcoming (event date > now)
        - event organizer has setup Stripe payouts to receive payments from ticket purchases
        - event has available seats

    Event annotations:
        - lowest_price
        - total seats & seats sold
        - percent_sold
        - "Hot" badge for events with >80% seats sold
    """

    events = Event.objects.filter(
        date__gte=timezone.now(),
        organizer__stripe_account__stripe_account_ready=True
        ).annotate(
        lowest_price=ExpressionWrapper(
            Min('price_zones__price'),
            output_field=FloatField()
        ),

        event_seats=Sum('price_zones__seats'),
        event_seats_sold=Sum('price_zones__seats_sold')
    ).annotate(

        percent_sold=ExpressionWrapper(
            F('event_seats_sold') * 1.0 / F('event_seats'),
            output_field=FloatField()
        ),

        badge=Case(
            When(percent_sold__gt=0.8, then=Value('Hot')),
            default=Value(''),
        )
    ).filter(event_seats_sold__lt=F('event_seats')).distinct()

    return render(request, 'events/view-events.html', {'events': events})


@login_required
def create_event(request):      # pylint: disable=too-many-locals
    """
    Handle event creation.

    GET:
        - Serve create event form page.

    POST:
        Validate submitted form.
        - On errors:
            - Return create event form form with errors.
        - On success:
            - Create event object (Event) with the validated provided details.
            - Create price zone objects (EventPriceZone) associated with the event.
            - Create image objects (EventImage) associated with the event.
            - Redirect to event page.
    """

    if request.method == "POST":
        user = request.user
        event_form = EventInfoValidator(request.POST)
        image_form = EventImageValidator(request.POST, request.FILES)
        price_zone_forms = PriceZoneFormSet(request.POST, prefix="zones")

        if ( event_form.is_valid() and image_form.is_valid() and price_zone_forms.is_valid() ):

            # concatenate date and time
            user_tz = ZoneInfo(event_form.cleaned_data['timezone'])
            event_user_local_datetime = timezone.make_aware(
                datetime.combine(
                    event_form.cleaned_data['date'],
                    event_form.cleaned_data['time']
                ),
                user_tz
            )
            event_utc_datetime = event_user_local_datetime.astimezone(dt_timezone.utc)

            # create event object
            event = Event.objects.create(
                name=event_form.cleaned_data['name'],
                date=event_utc_datetime,
                location=event_form.cleaned_data['location'],
                category=event_form.cleaned_data['category'],
                description=event_form.cleaned_data['description'],
                organizer=user
            )

            # create price zone object
            for zone in price_zone_forms.cleaned_data:
                if zone:
                    EventPriceZone.objects.create(
                        event=event,
                        name=zone['zone_name'],
                        desc=zone['zone_desc'],
                        price=zone['zone_price'],
                        seats=zone['zone_seats']
                    )

            # upload images and create image objects
            try:
                images = image_form.cleaned_data.get('images', [])
                fs = FileSystemStorage()

                for img in images:
                    file = fs.save(img.name, img)
                    file_path = fs.path(file)
                    url = cloud_upload_img(file_path)
                    fs.delete(file)

                    EventImage.objects.create(
                        event=event,
                        url = url
                    )
            except Exception:       # pylint: disable=broad-exception-caught
                event_form.add_error('images', "Something went wrong.")

            return redirect('events:view_event', event_id=event.id)
    else:
        event_form = EventInfoValidator()
        image_form = EventImageValidator()
        price_zone_forms = PriceZoneFormSet(prefix="zones")

    return render(request, 'events/create-event.html', {
            'event_form': event_form,
            'image_form': image_form,
            'price_zone_forms': price_zone_forms
        })


def view_event(request, event_id):
    """
    Display single event's information.

    Additional behavior:
        - Hide event from anyone except organizer if organizer’s Stripe account is not setup.
        - If user owns tickets to this event, preview it.
        - On POST validate order information before proceeding to checkout.

    Args:
        request (HttpRequest)
        event_id (int): ID of the event to view.
    """

    event = get_object_or_404(Event, id=event_id)

    if (event.organizer != request.user and not event.organizer.stripe_account.stripe_account_ready):
        raise Http404("Event not found")

    image_urls = []
    images = event.images.all()
    for image in images:
        image_urls.append(image.url)

    owned_tickets = None
    if request.user.is_authenticated:
        owned_tickets = Ticket.objects.filter(
            order__acquirer=request.user,
            price_zone__event=event
        )

    if request.method == "POST":
        form = OrderFormValidator(request.POST)

        # check if user attempts to purchase tickets for past event
        if event.is_past:
            form.add_error(None, "This event has already ended. Tickets cannot be purchased.")

        # check if event owner has setup payouts
        get_stripe_account(request.user)
        if not event.organizer.stripe_account.stripe_account_ready:
            form.add_error(None, "Event owner has not configured their bank settings to receive payments.")

        if not event.is_past and form.is_valid():
            selected_tickets = form.cleaned_data.get('price_zones', [])
            request.session['selected_tickets'] = selected_tickets
            request.session['selected_event'] = event.id
            return redirect('events:checkout', event_id=event.id)
    else:
        form = OrderFormValidator()

    return render(request, 'events/view-event.html', {
        'event': event,
        'stripe_account_ready': event.organizer.stripe_account.stripe_account_ready,
        'tickets_user_owns': owned_tickets,
        'imgs': image_urls, 
        'price_zones': event.price_zones.all(),
        'form': form
    })


@login_required
def edit_event(request, event_id):
    """
    Handle event update.

    Restrictions:
        - Only the event owner may edit.
        - Past events cannot be edited.

    GET:
        - Serve edit event form page with pre-filled event details.

    POST:
        Validate submitted form.
        - On errors:
            - Return edit event form form with errors.
        - On success:
            - Update event details (Event) with the updated and validated details.
            - Redirect to event page.
    """

    # users can modify details about their upcoming events
    event = get_object_or_404(Event, id=event_id, organizer=request.user, date__gte=timezone.now())

    if request.method == "POST":
        event_form = EventInfoValidator(request.POST)

        if event_form.is_valid():

            # concatenate date and time
            user_tz = ZoneInfo(event_form.cleaned_data['timezone'])
            event_user_local_datetime = timezone.make_aware(
                datetime.combine(
                    event_form.cleaned_data['date'],
                    event_form.cleaned_data['time']
                ),
                user_tz
            )
            event_utc_datetime = event_user_local_datetime.astimezone(dt_timezone.utc)

            # update event
            event.name=event_form.cleaned_data['name']
            event.date=event_utc_datetime
            event.location=event_form.cleaned_data['location']
            event.category=event_form.cleaned_data['category']
            event.description=event_form.cleaned_data['description']

            event.save()

            return redirect('events:view_event', event_id=event.id)
    else:
        event_form = EventInfoValidator(initial={
            'name': event.name,
            'date': event.date.date(),
            'time': event.date.time(),
            'location': event.location,
            'category': event.category,
            'description': event.description,
        })

    return render(request, 'events/edit-event.html', {
            'event': event, 
            'event_form': event_form
        })


@login_required
def checkout(request, event_id):
    """
    Handle payment for ticket purchases.

    Workflow:
        - Load selected tickets from session.
        - Compute totals (subtotal, service fee, tax, total).
        - If total = 0 (free tickets only): skip Stripe payment and auto-complete order.
        - If total > 0 (paid only or paid/free tickets):
            - Creates and confirms a Stripe PaymentIntent.
            - If confirmed  PaymentIntent is successful, saves Order and associated Tickets.

    Args:
        request (HttpRequest)
        event_id (int): ID of the event, which tickets are being purchased.
    """

    event = get_object_or_404(Event, id=event_id)

    if not event.organizer.stripe_account.stripe_account_ready:
        raise Http404("Event not found")

    selected_tickets = request.session.get('selected_tickets')
    selected_event = request.session.get('selected_event')
    if not selected_tickets or selected_event != event.id:
        return redirect('events:view_event', event_id=event.id)

    subtotal, service_fee, tax, total = _calculate_order_totals(selected_tickets)

    if total == 0:
        order = Order.objects.create(
            status="succeeded",
            stripePaymentId=None,
            acquirer=request.user,
            subtotal=subtotal,
            tax=tax,
            service_fee=service_fee,
            total=total
        )
        _save_tickets(selected_tickets, order)
        request.session.pop("selected_tickets")
        request.session.pop("selected_event")
        return redirect("events:checkout_success", event_id=event.id, order_id=order.id)

    if request.method == "POST":
        payment_method_id = request.POST.get("payment_method_id")

        try:
            confirmed_intent = _create_and_confirm_payment(total, payment_method_id, request.user.email)

            # save order to db
            order = Order.objects.create(
                status = confirmed_intent.status,
                stripePaymentId = confirmed_intent.id,
                acquirer = request.user,
                subtotal = subtotal,
                tax = tax,
                service_fee = service_fee,
                total = total
            )

            if confirmed_intent.status == "succeeded":
                # TODO send money to the event owner

                # save tickets in db
                purchased_tickets = request.session.pop("selected_tickets")
                _save_tickets(purchased_tickets, order)

                return redirect("events:checkout_success", event_id=event.id, order_id=order.id)
            return redirect("events:checkout_fail", event_id=event.id, order_id=order.id)

        except (stripe.StripeError, Exception):     # pylint: disable=broad-exception-caught
            return redirect("events:checkout_fail", event_id=event.id, order_id=order.id)

    return render(request, 'events/checkout.html', {
        'event': event,
        'selected_tickets': selected_tickets,
        'subtotal': subtotal,
        'service_fee': service_fee,
        'tax': tax,
        'total': total,
        'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY
    })


@login_required
def checkout_success(request, event_id, order_id):
    """
    Display the payment success page.

    Redirects to the event page or payment fail page if the check fails.
    Otherwise displays payment success page.

    Validates:
        - order_id: belongs to the logged in user
        - payment succeeded: otherwise redirects to payment fail page

    Args:
        event_id (int): ID of the event for which the order was made.
        order_id (int): ID of the order that was made by the user and is successful.
    """

    event = get_object_or_404(Event, id=event_id)
    order = get_object_or_404(Order, id=order_id, acquirer=request.user)

    if order.status != 'succeeded':
        return redirect('events:checkout_fail', event_id=event.id, order_id=order.id)

    purchased_tickets = (
        order.tickets
        .values("price_zone__name")
        .annotate(quantity=Count("id"))
    )

    return render(request, 'events/payment-success.html', {
        'event': event, 
        'order': order,
        'purchased_tickets': purchased_tickets
    })


@login_required
def checkout_fail(request, event_id, order_id):
    """
    Display the payment fail page.

    Redirects to the event page or payment success page if the check approves.
    Otherwise displays payment fail page.

    Validates:
        - order_id: belongs to the logged in user
        - payment did not succeed: otherwise redirects to payment success page

    Args:
        event_id (int): ID of the event for which the order was made.
        order_id (int): ID of the order that was made by the user and has failed.
    """

    event = get_object_or_404(Event, id=event_id)
    order = get_object_or_404(Order, id=order_id)

    # users cannot see orders that are not their own
    if order.acquirer != request.user:
        return redirect("events:view_event", event_id=event.id)

    if order.status == 'succeeded':
        return redirect('events:checkout_success', event_id=event.id, order_id=order.id)
    return render(request, 'events/payment-fail.html')


@login_required
def my_events(request):
    """Display all events created by the logged-in user."""
    all_events = request.user.events.all()
    return render(request, 'events/my-events.html', { 'events': all_events })
