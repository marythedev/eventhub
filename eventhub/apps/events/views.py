import os
import json
import stripe
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

from .models import *
from .forms import EventInfoValidator, EventImageValidator, PriceZoneFormSet, OrderFormValidator, CheckoutForm
from users.utils import cloud_upload_img

# environmental variables
CDN_DOMAIN = settings.CDN_DOMAIN
SERVICE_FEE = settings.SERVICE_FEE
TAX = settings.TAX
STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

# helper functions
def _round(number):
    return Decimal(number).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


# views
@login_required
def create_event(request):
    """
    Handle event creation.

    GET:
        - Serve create event form page.

    POST:
        Validate submitted form.
        - On errors:
            - Return create event form form with errors
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
            
            # create event object
            event = Event.objects.create(
                name=event_form.cleaned_data['name'],
                date=event_form.cleaned_data['date'],
                time=event_form.cleaned_data['time'],
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

# TODO: dynamic event rendering + filtering
def view_events(request):
    file_path = os.path.join(settings.APP_ROOT,'apps', 'events', 'data', 'dummy_data.json')
    with open(file_path, "r") as f:
        dummy_data = json.load(f)
    return render(request, 'events/view-events.html', {'events': dummy_data, 'CDN_DOMAIN': CDN_DOMAIN})

@login_required
def checkout(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    selected_tickets = request.session.get('selected_tickets')
    
    if not selected_tickets:
        return redirect('events:view_event', event_id=event.id)
    
    # accumulate the price summary for selected tickets
    subtotal = Decimal(0)
    for ticket in selected_tickets:
        subtotal += Decimal(ticket.get("total"))
    
    subtotal = _round(subtotal)
    service_fee = _round( subtotal * Decimal(SERVICE_FEE) )
    tax = _round( subtotal * Decimal(TAX) )
    total = _round( subtotal + service_fee + tax )

    if request.method == "POST":
        payment_method_id = request.POST.get("payment_method_id")

        try:
            # payment intent based on received payment_method_id from frontend
            stripe.api_key = STRIPE_SECRET_KEY
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency="usd",
                payment_method=payment_method_id,
                automatic_payment_methods={"enabled": True, "allow_redirects": "never"}
            )
                        
            # payment confirmation
            confirmed_intent = stripe.PaymentIntent.confirm(
                payment_intent.id,
                payment_method=payment_method_id
            )
            
            print(confirmed_intent.status)
            request.session["payment_status"] = confirmed_intent.status
            if confirmed_intent.status == "succeeded":
                request.session.pop("selected_tickets", None)
                # update ticket quantity here, make tickets assiciated with user
                # send money to the event owner
                print("success")
                return redirect("events:payment_success", event_id=event.id)
            else:
                print('failed')
                return redirect("events:payment_fail", event_id=event.id)
        
        except stripe.StripeError as e:
            # Generic Stripe error
            print("Stripe error:", e)
            return redirect("events:payment_fail", event_id=event.id)
        
        except Exception as e:
            print("Other error:", e)
            return redirect("events:payment_fail", event_id=event.id)

        
    else:
        form = CheckoutForm()
    
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
def payment_success(request, event_id):
    """
    Display the payment success page.

    Validates:
        - payment_status: to make sure user did not just typed in the url; otherwise redirects to event page
            - payment_status is generated by system on checkout
        - payment succeeded: otherwise redirects to payment fail page
    
    Redirects to the event page or payment fail page if the check fails otherwise displays payment success page.
    """
    
    event = get_object_or_404(Event, id=event_id)
    
    payment_status = request.session.get("payment_status", None)
    if not payment_status:
        return redirect('events:view_event', event_id=event.id)
    
    if payment_status != 'succeeded':
        return redirect('events:payment_fail', event_id=event.id)
    
    request.session.pop("payment_status", None)
    return render(request, 'events/payment-success.html')

@login_required
def payment_fail(request, event_id):
    """
    Display the payment fail page.

    Validates:
        - payment_status: to make sure user did not just typed in the url; otherwise redirects to event page
            - payment_status is generated by system on checkout
        - payment did not succeed: otherwise redirects to payment success page
    
    Redirects to the event page or payment success page if the check approves otherwise displays payment fail page.
    """
    
    event = get_object_or_404(Event, id=event_id)
    
    payment_status = request.session.get("payment_status", None)
    if not payment_status:
        return redirect('events:view_event', event_id=event.id)
    
    if payment_status == 'succeeded':
        return redirect('events:payment_success', event_id=event.id)
    
    request.session.pop("payment_status", None)
    return render(request, 'events/payment-fail.html')