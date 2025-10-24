import os
import io
import json
from dotenv import load_dotenv
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

from .models import *
from .forms import EventInfoValidator, EventImageValidator, PriceZoneFormSet
from users.utils import cloud_upload_img

load_dotenv()

# TODO: home page for logged in user
def home(request):
    return render(request, 'core/home.html')

# TODO: dynamic event rendering + filtering
def explore(request):
    file_path = os.path.join(settings.APP_ROOT,'apps', 'core', 'data', 'dummy_data.json')
    with open(file_path, "r") as f:
        dummy_data = json.load(f)
    return render(request, 'core/explore-events.html', {'events': dummy_data, 'CDN_DOMAIN': os.getenv('CDN_DOMAIN')})


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
                seating_type=event_form.cleaned_data['seating_type'],
                organizer=user
            )
            
            # create price zone object
            for zone in price_zone_forms.cleaned_data:
                if (zone):
                    EventPriceZone.objects.create(
                        event=event,
                        zone_name=zone['zone_name'],
                        zone_price=zone['zone_price'],
                        zone_seats=zone['zone_seats']
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
                        image_url = url
                    )
            except Exception:
                event_form.add_error('images', "Something went wrong.")

            # TODO: on success redirect to event page
    else:
        event_form = EventInfoValidator()
        image_form = EventImageValidator()
        price_zone_forms = PriceZoneFormSet(prefix="zones")
    
    return render(request, 'core/create-event.html', {
            'event_form': event_form,
            'image_form': image_form,
            'price_zone_forms': price_zone_forms
        })
