import os
import json
from dotenv import load_dotenv
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Event
from .forms import CreateEventValidator

load_dotenv()


def home(request):
    return render(request, 'core/home.html')

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
        - Create an event with the validated provided information.
        - Return register form with errors or redirect to event page. 
    """

    if request.method == "POST":
        user = request.user
        form = CreateEventValidator(request.POST)
        if form.is_valid():
            Event.objects.create(
                event_name=form.cleaned_data['event_name'],
                event_date=form.cleaned_data['event_date'],
                event_time=form.cleaned_data['event_time'],
                event_location=form.cleaned_data['event_location'],
                event_category=form.cleaned_data['event_category'],
                event_description=form.cleaned_data['event_description'],
                organizer=user
            )
            
            # TODO: on success redirect to event page
    else:
        form = CreateEventValidator
    return render(request, 'core/create-event.html', {'form': form})
