import os
import json
import stripe
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.utils import timezone
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Count

from .models import *
from tickets.models import *

from .forms import EventInfoValidator, EventImageValidator, PriceZoneFormSet, OrderFormValidator, CheckoutForm
from users.utils import cloud_upload_img

# environmental variables
CDN_DOMAIN = settings.CDN_DOMAIN
SERVICE_FEE = settings.SERVICE_FEE
TAX = settings.TAX
STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY


# round decimal number up if it is more than 0.5
def _round(number):
    return Decimal(number).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# accumulate the price summary for selected tickets
def _calculate_order_totals(selected_tickets):
    subtotal = Decimal(0)
    for ticket in selected_tickets:
        subtotal += Decimal(ticket.get("total"))
    
    subtotal = _round(subtotal)
    service_fee = _round( subtotal * Decimal(SERVICE_FEE) )
    tax = _round( subtotal * Decimal(TAX) )
    total = _round( subtotal + service_fee + tax )
    return subtotal, service_fee, tax, total

# payment from customer to Eventhub via Stripe
def _create_and_confirm_payment(total, payment_method_id, user_email):
    # payment intent based on received payment_method_id from frontend
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

# save tickets to db and associate them with order
# update ticket quantity for the event (tickets have been purchased)
def _save_tickets(purchased_tickets, order):
    for t in purchased_tickets:
        price_zone = EventPriceZone.objects.filter(id=t.get("id")).first()                 
        if price_zone:
            for _ in range(t.get('quantity')):
                Ticket.objects.create(
                    price_zone = price_zone,
                    order = order
                )



# views
# TODO: dynamic event rendering + filtering
def view_events(request):
    file_path = os.path.join(settings.APP_ROOT,'apps', 'events', 'data', 'dummy_data.json')
    with open(file_path, "r") as f:
        dummy_data = json.load(f)
    return render(request, 'events/view-events.html', {'events': dummy_data, 'CDN_DOMAIN': CDN_DOMAIN})


@login_required
def create_event(request):
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
            event_datetime = timezone.make_aware(
                datetime.combine(
                    event_form.cleaned_data['date'], 
                    event_form.cleaned_data['time']
                ),
                timezone.get_current_timezone()
            )
            
            # create event object
            event = Event.objects.create(
                name=event_form.cleaned_data['name'],
                date=event_datetime,
                location=event_form.cleaned_data['location'],
                category=event_form.cleaned_data['category'],
                description=event_form.cleaned_data['description'],
                organizer=user
            )
            
            # create price zone object
            for zone in price_zone_forms.cleaned_data:
                if (zone):
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
            except Exception:
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
    event = get_object_or_404(Event, id=event_id)
    
    image_urls = []
    images = event.images.all()
    for image in images:
        image_urls.append(image.url)
        
    if request.method == "POST":
        form = OrderFormValidator(request.POST)
        
        if form.is_valid():
            selected_tickets = form.cleaned_data.get('price_zones', [])
            request.session['selected_tickets'] = selected_tickets
            return redirect('events:checkout', event_id=event.id)
    else:
        form = OrderFormValidator()
    
    return render(request, 'events/view-event.html', {
        'event': event, 
        'imgs': image_urls, 
        'price_zones': event.price_zones.all(),
        'form': form
    })

@login_required
def edit_event(request, event_id):
    """
    Handle event update.

    GET:
        - Serve edit event form page.

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
        
        if ( event_form.is_valid()):
            
            # concatenate date and time
            event_datetime = timezone.make_aware(
                datetime.combine(
                    event_form.cleaned_data['date'], 
                    event_form.cleaned_data['time']
                ),
                timezone.get_current_timezone()
            )
            
            # update event 
            event.name=event_form.cleaned_data['name']
            event.date=event_datetime
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
    event = get_object_or_404(Event, id=event_id)
    
    selected_tickets = request.session.get('selected_tickets')
    if not selected_tickets:
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
            else:
                return redirect("events:checkout_fail", event_id=event.id, order_id=order.id)
        
        except (stripe.StripeError, Exception):
            return redirect("events:checkout_fail", event_id=event.id, order_id=order.id)

    else:
        form = CheckoutForm() # TODO
    
    return render(request, 'events/checkout.html', {
        'event': event,
        'selected_tickets': selected_tickets,
        'subtotal': subtotal,
        'service_fee': service_fee,
        'tax': tax,
        'total': total,
        'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY,
        'form': form
    })

@login_required
def checkout_success(request, event_id, order_id):
    """
    Display the payment success page.

    Validates:
        - order_id: belongs to the logged in user
        - payment succeeded: otherwise redirects to payment fail page
    
    Redirects to the event page or payment fail page if the check fails otherwise displays payment success page.
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

    Validates:
        - order_id: belongs to the logged in user
        - payment did not succeed: otherwise redirects to payment success page
    
    Redirects to the event page or payment success page if the check approves otherwise displays payment fail page.
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
    """View events created by the user."""
    
    all_events = request.user.events.all()
    
    return render(request, 'events/my-events.html', { 'events': all_events })