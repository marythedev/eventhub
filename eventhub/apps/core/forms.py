
from django import forms
from django.core.exceptions import ValidationError
from datetime import date, datetime

from .models import Event
from users.utils import validate_location

class CreateEventValidator(forms.Form):
    """
    Validates event creation information.

    Fields:
        event_name (str): Name of the event, required.
        event_date (date): Date of the event, must be today or later.
        event_time (time): Start time of the event, required.
        event_location (str): Full address, required.
        event_category (str): Event category from predefined choices.
        event_description (str): Optional text describing the event.

    Returns:
        dict: Cleaned and validated data.
    """
    
    event_name =  forms.CharField(
        required=True,
        max_length=100,
        error_messages={
            'required': 'Event name is required.',
            'max_length': 'Event name cannot exceed 100 characters.'
        }
    )
    event_date = forms.DateField(
        required=True,
        error_messages={'required': 'Event date is required.'}
    )
    event_time = forms.TimeField(
        required=True,
        error_messages={'required': 'Event time is required.'}
    )
    event_location = forms.CharField(
        required=True,
        max_length=255,
        error_messages={
            'required': 'Event location is required.',
            'max_length': 'Location length exceeded.'
        }
    )
    event_category = forms.ChoiceField(
        required=True,
        choices=Event.CATEGORIES,        
        error_messages={
            'required': 'Event category is required.',
            'invalid_choice': 'Select a valid event category.'
        }
    )
    event_description = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            'max_length': 'Description cannot exceed 5000 characters.'
        }
    )
    
    # check that event date is not in the past
    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < date.today():
            raise ValidationError("Event date cannot be in the past.")
        return event_date

    def clean_event_location(self):
        event_location = self.cleaned_data.get('event_location')
        
        if event_location:
            event_location = validate_location(event_location)
            
            # update location on form
            self.data = self.data.copy()
            self.data['event_location'] = event_location
        
        return event_location

    # check that event time is not in the past
    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get("event_date")
        event_time = cleaned_data.get("event_time")

        if event_date == date.today() and event_time:
            now = datetime.now().time()
            if event_time < now:
                self.add_error('event_time', "Event time cannot be in the past.")

        return cleaned_data
