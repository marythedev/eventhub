from django import forms
from django.contrib.auth.forms import SetPasswordForm
from users.forms import email_field, full_name_field, validate_password


class PasswordResetValidator(SetPasswordForm):
    """
    Validates passwords against password complexity rules.

    Inherits:
        SetPasswordForm: The default Django form for resetting a user's password.
    """

    def clean_new_password1(self):
        """Check new password against the password validation rules."""
        password = self.cleaned_data.get('new_password1')
        validate_password(password)
        return password

class ContactInquiryValidator(forms.Form):
    """
    Validates contact form data.

    Fields:
        full_name (str): User's full name, max length 100, required.
        email (str): User's email address, required.
        message (str): Description of the inquiry, max length 1500, required.

    Returns:
        dict: Cleaned data containing validated form input.
    """

    full_name = full_name_field()
    email = email_field()
    message = forms.CharField(
        required=True,
        max_length=1500,
        error_messages={
            'max_length': 'Description cannot exceed 1500 characters.'
        }
    )
