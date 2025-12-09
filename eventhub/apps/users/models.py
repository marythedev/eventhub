from core.utils.image_utils import cloud_delete_img
from core.utils.stripe_utils import delete_stripe_account
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ProfileManager(BaseUserManager):
    """
    Manager for the Profile model.
    Provides methods to:
        - create regular users
        - create superusers
        - check user existence
    """

    def create_user(self, email, full_name, password=None, **extra_fields):
        """
        Creates a regular user.

        Args:
            email (str, required, unique): User's email address.
            full_name (str): User's full name.
            password (str): Password to set for the user.
            extra_fields (dict): Additional fields passed to the user model.

        Raises:
            ValueError: If email is not provided.

        Returns:
            user (Profile): The newly created user instance.
        """

        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """
        Creates a superuser with full permissions (is_staff and is_superuser are set to True).

        Args:
            email (str): Admin's email address.
            full_name (str): Admin's full name.
            password (str): Password to set for the admin user.
            extra_fields (dict): Additional fields passed to the user model.

        Returns:
            user (Profile): The newly created superuser.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)

    def user_exists(self, email, ignore_user_id=None):
        """
        Checks if a user with the specified email exists.

        Args:
            email (str): Email to check.
            ignore_user_id (int, optional): User (primary key) to exclude from the check.
                Useful when updating the current user's email.

        Returns: True if another user with the email exists, False otherwise.
        """

        email = self.normalize_email(email)
        query = self.model.objects.filter(email = email)
        if ignore_user_id:
            query = query.exclude(pk = ignore_user_id)
        return query.exists()


class Profile(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model. Uses email as unique identifier.

    Inherits:
        AbstractBaseUser (handles password and login tracking)
        PermissionsMixin (adds permission support).

    Fields:
        avatar (URLField): URL to user's avatar image.
        email (EmailField): Unique email used for authentication.
        full_name (CharField): User's full name.
        phone (CharField): Optional phone number.
        location (CharField): Optional location string.
        location_lat (float): Optional location latitude value.
        location_lon (float): Optional location longitude value.
        is_active (bool): Account activation status.
        is_staff (bool): Admin site access status.
    """

    avatar = models.URLField(blank=True, null=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    location_lat = models.FloatField(blank=True, null=True)
    location_lon = models.FloatField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']     # for superuser (for regular user it is auto required)

    objects = ProfileManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Returns user's full name."""
        return self.full_name

    def get_short_name(self):
        """Returns: first name (before space) or defaults to full name if no space."""
        return self.full_name.split()[0]

    def delete(self, *args, **kwargs):
        """
        Delete profile.

        Profile cannot be deleted if user has events for which payouts were not released.
        Profile is soft deleted if user has orders and/or upcoming events for tickets were sold.
        Profile is deleted if it has no orders and events associated with it.
        """

        upcoming_events_with_revenue = self.events.filter(
            date__gte=timezone.now(),
            price_zones__revenue__gt=0
        ).distinct()

        if upcoming_events_with_revenue:
            raise ValidationError("Account cannot be deleted because there are upcoming events with sold tickets.")

        cloud_delete_img(self.avatar)

        # delete user events with no orders
        for event in self.events.all():
            try:
                event.delete()
            except ValidationError:
                pass    # event cannot be deleted because it has sold tickets

        user_has_events = self.events.exists()
        user_has_orders = self.orders.exists()

        if (user_has_events or user_has_orders):
            self.is_active = False
            self.avatar = None
            self.full_name = "Deleted User"
            self.phone = None
            self.location = None
            self.location_lat = None
            self.location_lon = None
            self.save()

            delete_stripe_account(self)

        else:
            super().delete(*args, **kwargs)


class StripeAccount(models.Model):
    """
    Users's Stripe Account.
    Each user can have only one Stripe account.

    Fields:
        stripe_account_id (CharField): Stripe account ID (generated by Stripe).
        stripe_account_ready (bool): Whether all account details are submitted,
            payouts are fully configured and account is ready.
        account_owner (Profile): The user who owns this Stripe account.
    """

    stripe_account_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    stripe_account_ready = models.BooleanField(default=False)

    account_owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stripe_account',
    )

    def __str__(self):
        return f"{self.account_owner.email} Stripe Account"
