from django.contrib.auth.forms import SetPasswordForm
from users.forms import validate_password


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
