from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import re
from .models import Profile

class RegisterFormValidator(forms.Form):
    """
    Validates user registration data.

    Args:
        full_name (str): User's full name, max length 100.
        email (str): User's email address, must be unique.
        password (str): User's password, with complexity requirements.
        confirm_password (str): Confirmation of password, must match.
        terms_accepted (bool): Indicates acceptance of terms.

    Raises:
        ValidationError: Raised if any validation rule fails, such as missing fields, duplicate email,
                         weak password, passwords don't match, or terms not accepted.

    Returns:
        dict: Cleaned data containing containing validated form input.
    """
    
    full_name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'Full name is required.',
            'max_length': 'Full name length exceeded.'
        }
    )
    email = forms.EmailField(
        required=True,
        error_messages={'required': 'Email is required.'}
    )
    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput,
        error_messages={'required': 'Password is required.'}
    )
    confirm_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput,
        error_messages={'required': 'Confirm password is required.'}
    )
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

        return password

    # check if password and confirm_password match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


class LoginFormValidator(forms.Form):
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
    
    email = forms.EmailField(
        required=True,
        error_messages={'required': 'Email is required.'}
    )
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
