import os
import re
import requests
from dotenv import load_dotenv
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import Profile

load_dotenv()

# Helper functions
def _full_name_field():
    """Helper function that returns CharField with full name validation rules."""
    return forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'Full name is required.',
            'max_length': 'Full name length exceeded.'
        }
    )

def _email_field():
    """Helper function that returns EmailField with email validation rules."""
    return forms.EmailField(
        required=True,
        error_messages={'required': 'Email is required.'}
    )

def _password_field(required_message):
    """Helper function that returns CharField with password validation rules."""
    return forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'min_length': 'Password must be at least 8 characters long.',
            'required': required_message
        }
    )

def _validate_password(password):
    """
    Helper function to define password validation rules:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit
        - Contains at least one special character (@, $, !, %, *, ?, &)
    """
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[@$!%*?&]", password):
        raise ValidationError("Password must contain at least one special character (@, $, !, %, *, ?, &).")


# Validation forms
class RegisterValidator(forms.Form):
    """
    Validates user registration data.

    Args:
        full_name (str): User's full name, max length 100.
        email (str): User's email address, must be unique.
        password (str): User's password, must satisfy validation rules.
        confirm_password (str): Confirmation of password, must match the password.
        terms_accepted (bool): Indicates acceptance of terms.

    Raises:
        ValidationError: Raised if any validation rule fails, such as missing fields, duplicate email,
                         weak password, passwords don't match, or terms not accepted.

    Returns:
        dict: Cleaned data containing validated form input.
    """
    
    full_name = _full_name_field()
    email = _email_field()
    password = _password_field('Password is required.')
    confirm_password = _password_field('Confirm password is required.')
    terms_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'Please accept the Terms and Conditions.'}
    )

    # check if the email already exists in db
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.user_exists(email=email):
            raise ValidationError("Email is already registered.")
        return email

    # password validation rules
    def clean_password(self):
        password = self.cleaned_data.get('password')

        _validate_password(password)

        return password

    # check if password and confirm_password match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


class LoginValidator(forms.Form):
    """
    Validates user login credentials.

    Args:
        email (str): User's email address.
        password (str): User's password.


    Raises:
        ValidationError: Raised if fields are missing or credentials are invalid.

    Returns:
        dict: The authenticated user is stored in the form's cleaned data.
    """
    
    email = _email_field()
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
        error_messages={'required': 'Password is required.'}
    )

    # Authenticate user credentials
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise ValidationError("Invalid email or password.")

            cleaned_data["user"] = user

        return cleaned_data


class ProfileValidator(forms.Form):
    """
    Validates user's profile information for its further update.

    Fields:
        full_name (str): User's full name, required.
        email (str): User's email address, required must be unique.
        phone (str): Phone number that matches validation rules, optional.
        location (str): Location that matches validation rule, optional.

    Args:
        user (Profile): The current user instance for whom information is being updated.

    Returns:
        dict: Cleaned data with validated and transformed (if needed) input.
    """
    
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    full_name = _full_name_field()
    email = _email_field()
    phone = forms.CharField(
        max_length=25,
        required=False,
        error_messages={
            'max_length': 'Phone number is too long.'
        }
    )
    location = forms.CharField(
        max_length=255,
        required=False,
        error_messages={
            'max_length': 'Location length exceeded.'
        }
    )
    
    # check if the new email already exists in db, excluding current user's email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.user.email and Profile.objects.user_exists(email=email, ignore_user_id = self.user.pk):
            raise ValidationError("Email is already registered.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        if phone and phone != self.user.phone:
            # remove formatting characters - parentheses, dashes, and spaces for consistent phone format
            phone = re.sub(r'[()\-\s]', '', phone)
            
            # phone validation rules
            phone_digits = phone[1:]    # grab the numeric part of the phone number (exclude "+" at the beginning)
            if not phone.startswith('+'):
                raise ValidationError("Phone number must start with a '+'.")
            if not phone_digits.isdigit():
                raise ValidationError("Phone number is invalid.")   # contains letters
            if len(phone_digits) < 6:
                raise ValidationError("Phone number is too short.")
            if len(phone_digits) > 15:
                raise ValidationError("Phone number is too long.")
        
        return phone
    
    # location validation rule
    def clean_location(self):
        location = self.cleaned_data.get('location')
        
        if location and location != self.user.location:
            try:
                # fetch openstreetmap to check if location exists
                response = requests.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={'q': location, 'format': 'json'},
                    headers={
                        'User-Agent': f'Eventhub/{os.getenv("APP_VERSION", "1.0")}',
                        'Accept-Language': 'en'
                    }
                )
                data = response.json()
                
                if len(data) == 0:
                    raise ValidationError("Location not found. Please enter a valid place.")

                # transform location to full display name for consistent location format
                location = data[0]['display_name']
                
            except ValidationError:
                raise
            except Exception:
                raise ValidationError("Failed to validate location. Try again later.")
            
        return location
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class SecurityValidator(forms.Form):
    """
    Validates user's security information for its further update.

    Fields:
        current_password (str): User's current password.
        new_password (str): User's new password, must satisfy validation rules.
        confirm_new_password (str): Confirmation of password, must match the new password.

    Args:
        user (Profile): The current user instance for whom information is being updated.

    Returns:
        dict: Cleaned data containing validated form input.
    """

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    current_password = _password_field('Current password is required.')
    new_password = _password_field('New password is required.')
    confirm_new_password = _password_field('Confirmation of the new password is required.')
    
    # check new password again the password validation rules
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')

        _validate_password(new_password)

        return new_password

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        # check if new password and confirm new password match
        if new_password and confirm_new_password and new_password != confirm_new_password:
            self.add_error('confirm_new_password', "Passwords do not match.")
        
        # check if entered current password is correct
        if current_password and not self.user.check_password(current_password):
            self.add_error('current_password', "Current password is incorrect.")
        
        return cleaned_data
