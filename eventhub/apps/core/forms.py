
from django import forms
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from datetime import date as d, datetime

from .models import Event
from users.utils import validate_location, is_valid_image_format, MAX_FILE_SIZE_MB


class EventInfoValidator(forms.Form):
    """
    Validates event information for event (Event) creation.

    Fields:
        name (str): Name of the event, required.
        date (date): Date of the event, must be today or later.
        time (time): Start time of the event, required.
        location (str): Full address, required.
        category (str): Event category from predefined choices.
        description (str): Description of the event, optional.
        seating_type (str): Seating type of the event (general or reserved), required.
        
    Returns:
        dict: Cleaned and validated data.
    """
    
    name =  forms.CharField(
        required=True,
        max_length=50,
        error_messages={
            'required': 'Event name is required.',
            'max_length': 'Event name cannot exceed 100 characters.'
        }
    )
    date = forms.DateField(
        required=True,
        error_messages={'required': 'Event date is required.'}
    )
    time = forms.TimeField(
        required=True,
        error_messages={'required': 'Event time is required.'}
    )
    location = forms.CharField(
        required=True,
        max_length=255,
        error_messages={
            'required': 'Event location is required.',
            'max_length': 'Location length exceeded.'
        }
    )
    category = forms.ChoiceField(
        required=True,
        choices=Event.CATEGORIES,        
        error_messages={
            'required': 'Event category is required.',
            'invalid_choice': 'Select a valid event category.'
        }
    )
    description = forms.CharField(
        required=False,
        max_length=5000,
        error_messages={
            'max_length': 'Description cannot exceed 5000 characters.'
        }
    )
    seating_type = forms.ChoiceField(
        required=True,
        choices=Event.SEATING_TYPES,
        error_messages={
            'required': 'Seating type is required.',
            'invalid_choice': 'Select a valid seating type.'
        }
    )
    
    # check that event date is not in the past
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < d.today():
            raise ValidationError("Event date cannot be in the past.")
        return date

    def clean_location(self):
        location = self.cleaned_data.get('location')
        
        if location:
            location = validate_location(location)
            
            # update location on form
            self.data = self.data.copy()
            self.data['location'] = location
        
        return location

    def clean(self):
        cleaned_data = super().clean()
        
        # check that event time is not in the past
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        
        if date == d.today() and time:
            now = datetime.now().time()
            if time < now:
                self.add_error('time', "Event time cannot be in the past.")
        
        return cleaned_data


class EventImageValidator(forms.Form):
    """
    Validates event images for event (Event) creation.

    Fields:
        images (file): Uploaded image files of the event, required.
    
    Validation rules:
        - At least one image is uploaded.
        - Each uploaded image is in a supported format (JPG, PNG, GIF, WEBP).
        - Each image file does not exceed the maximum allowed size.
        
    Returns:
        dict: Cleaned and validated image data.
    """
    
    images = forms.FileField(
        required=True,
        error_messages={
            'required': 'At least one image of the event is required.'
        }
    )
    
    # backend validation for event images
    def clean_images(self):
        images = self.files.getlist('images')

        for image in images:
            if not is_valid_image_format(image):
                raise ValidationError(f"{image.name} has unsupported image format. Please upload a JPG, PNG, GIF or WEBP file.")

            if image.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"{image.name} image file is too large (max {MAX_FILE_SIZE_MB}MB).")

        return images


class PriceZoneValidator(forms.Form):
    """
    Validates event price zones for event (Event) creation.

    Fields:
        zone_name (str): The name of the price zone, required.
        zone_price (float): The price of the price zone in USD, required.
        zone_seats (int): The capacity of seats of the price zone, required.
        
    Returns:
        dict: Cleaned and validated price zone data.
    """
    
    zone_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            "required": True,
            "placeholder": "e.g. General Admission",
            "class": "zone-input",
            "inputmode": "numeric"
        }),
        error_messages={
            'required': 'Zone name is required.', 
            'max_length': 'Name cannot exceed 50 characters.'
        }
    )
    zone_price = forms.DecimalField(
        required=True,
        min_value=0,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            "required": True,
            "placeholder": "0.00",
            "class": "zone-price",
            "step": "0.01",
            "min": "0",
            "inputmode": "numeric"
        }),
        error_messages={
            'required': 'Price is required.', 
            'min_value': 'Price cannot be negative.'
        }
    )
    zone_seats = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={
            "required": True,
            "placeholder": "Seat capacity",
            "class": "zone-seats",
            "min": "1",
            "inputmode": "numeric",
        }),
        error_messages={
            'required': 'Seats capacity is required.', 
            'min_value': 'The minimum seat capacity for the price zone is 1.'
        }
    )

# formset to handle multiple PriceZoneValidator forms (user can add as many price zones for the new event as needed)
PriceZoneFormSet = formset_factory(PriceZoneValidator, extra=0, min_num=1, validate_min=True, can_delete=True)
