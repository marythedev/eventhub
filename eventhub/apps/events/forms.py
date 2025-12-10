
from datetime import date as d
from datetime import datetime
from zoneinfo import available_timezones

from core.utils.image_utils import is_valid_image_format
from core.utils.location_utils import clean_and_update_location
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import JSONField, formset_factory
from users.models import Profile

from .models import Event, EventPriceZone

MAX_UPLOAD_MB = settings.MAX_UPLOAD_MB

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
    timezone = forms.CharField(required=True)
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
    allow_reentry = forms.BooleanField(required=False, initial=False)

    def clean_date(self):
        """Check that event date is not in the past."""
        date = self.cleaned_data.get('date')
        if date and date < d.today():
            raise ValidationError("Event date cannot be in the past.")
        return date

    def clean_timezone(self):
        """
        Check that timezone sent with the form is valid.
        This is the protection from frontend dev tools manipulation.
        """

        timezone  = self.cleaned_data["timezone"]
        if timezone not in available_timezones():
            self.add_error('timezone', "Something went wrong. Refresh the page and try to submit the form again.")

        return timezone

    def clean_location(self):
        """
        Validate and normalize event location.
        If location is valid, get its latitude and longitude.
        """

        location = self.cleaned_data.get('location')

        if location:
            location = clean_and_update_location(self, location)

        return location

    def clean(self):
        """Check that event time is not in the past for today's events."""
        cleaned_data = super().clean()

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
        - Each uploaded image is in a supported format (JPG, PNG, WEBP).
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

    def clean_images(self):
        """Backend validation for each uploaded event image file."""

        images = self.files.getlist('images')
        for image in images:
            if not is_valid_image_format(image):
                raise ValidationError(
                    f"{image.name} has unsupported image format. Please upload a JPG, PNG or WEBP file."
                )

            if image.size > MAX_UPLOAD_MB * 1024 * 1024:
                raise ValidationError(f"{image.name} image file is too large (max {MAX_UPLOAD_MB}MB).")

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
        max_length=30,
        widget=forms.TextInput(attrs={
            "required": True,
            "placeholder": "e.g. General Admission",
            "class": "zone-input",
            "inputmode": "text"
        }),
        error_messages={
            'required': 'Name is required.', 
            'max_length': 'Name cannot exceed 30 characters.'
        }
    )
    zone_desc = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            "required": True,
            "placeholder": "Brief description of the price zone",
            "class": "zone-input",
            "inputmode": "text"
        }),
        error_messages={
            'required': 'Brief description is required.', 
            'max_length': 'Description cannot exceed 50 characters.'
        }
    )
    zone_price = forms.DecimalField(
        required=True,
        min_value=0,
        decimal_places=2,
        max_digits=7,
        max_value=99999.99,
        widget=forms.NumberInput(attrs={
            "required": True,
            "placeholder": "0.00 (USD)",
            "class": "zone-price",
            "step": "0.01",
            "inputmode": "numeric"
        }),
        error_messages={
            'max_value': 'Ticket price cannot exceed 99 999.99 USD.',
            'required': 'Price is required.', 
            'min_value': 'Price cannot be negative.'
        }
    )
    zone_seats = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=1000000,
        widget=forms.NumberInput(attrs={
            "required": True,
            "placeholder": "Seat capacity",
            "class": "zone-seats",
            "inputmode": "numeric",
        }),
        error_messages={
            'required': 'Seats capacity is required.', 
            'min_value': 'Minimum seat capacity is 1.',
            'max_value': 'Seat capacity cannot exceed 1 000 000 seats.'
        }
    )

# formset to handle multiple PriceZoneValidator forms (user can add as many price zones for the new event as needed)
PriceZoneFormSet = formset_factory(PriceZoneValidator, extra=0, min_num=1, validate_min=True, can_delete=True)


class TicketSelectionValidator(forms.Form):
    """
    Validates user selected tickets before checkout.

    Fields:
        price_zones (JSON): List of selected price zones with quantity.

    Validation:
        - At least one ticket must be selected.
        - Selected quantity does not exceed remaining seats for that price zone.
    """

    price_zones = JSONField(
        required=True,
        error_messages={
            'required': 'Select a ticket.',
            'invalid': 'Something is wrong. Try to refresh the page.'
        }
    )

    def clean_price_zones(self):
        """Validate ticket availability of selected price zones."""

        price_zones = self.cleaned_data.get('price_zones')
        selected_tickets = []
        for zone in price_zones:
            quantity = zone.get("quantity")

            # don't include the price zones that were not selected
            if quantity <= 0:
                continue

            try:
                zone = EventPriceZone.objects.get(id = zone.get("id"))
            except EventPriceZone.DoesNotExist:
                self.add_error('price_zones', "Could not find selected tickets. Try to refresh the page.")
                continue

            if zone.remaining_seats < quantity:
                self.add_error('price_zones', f"Selected quantity exceeds available {zone.name} tickets.")
                continue

            selected_tickets.append({
                "id": zone.id,
                "name": zone.name,
                "price": str(zone.price),
                "quantity": quantity,
                "total": str(zone.price * quantity)
            })

        return selected_tickets


class AddTeamValidator(forms.Form):
    """
    Validates a user to add to the event team.

    Fields:
        email (str): Email of the user to be added to the event team, required.

    Validation rules:
        - User must exist in the system.
        - The user cannot be the event organizer (organizer already has full privileges to the event).
        - The user must not already be a team member of the event.

    Returns:
        dict: Validated email of the team member to add.
    """

    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Enter a valid email address."
        }
    )

    def __init__(self, *args, **kwargs):
        """Get event information to which user is to be added."""
        self.event = kwargs.pop("event")
        super().__init__(*args, **kwargs)

    def clean_email(self):
        """Check if the user exists, is not the organizer or is not part of the team already."""

        email = self.cleaned_data["email"]

        try:
            user = Profile.objects.get(email=email)
        except Profile.DoesNotExist as e:
            raise ValidationError("No user found with this email.") from e

        if not user.is_active:
            raise ValidationError("This user has deleted their profile.")

        if user == self.event.organizer:
            raise ValidationError("As the organizer, you already part of the team.")

        if user in self.event.team.all():
            raise ValidationError("This user is already a team member.")

        return email


class RemoveTeamValidator(forms.Form):
    """
    Validates a user to remove from the event team.

    Fields:
        email (str): Email of the user to be removed from the event team, required.

    Validation rules:
        - User must exist in the system.
        - The user must currently be a team member of the event.

    Returns:
        dict: Validated email of the team member to remove.
    """

    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Enter a valid email address."
        }
    )

    def __init__(self, *args, **kwargs):
        """Get event information from which user is to be removed."""
        self.event = kwargs.pop("event")
        super().__init__(*args, **kwargs)

    def clean_email(self):
        """Check if the user exists, is the organizer and is part of the team."""
        email = self.cleaned_data["email"]

        try:
            user = Profile.objects.get(email=email)
        except Profile.DoesNotExist as e:
            raise ValidationError("No user found with this email.") from e

        if user not in self.event.team.all():
            raise ValidationError("This user is not part of the team.")

        return email
