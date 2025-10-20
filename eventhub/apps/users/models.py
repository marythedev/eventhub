from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class ProfileManager(BaseUserManager):
    """
    Manager for the Profile model.
    Provides methods to create regular users, superusers, and check user existence.
    """
    
    def create_user(self, email, full_name, password=None, **extra_fields):
        """Creates a regular user with unique email."""
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """Creates a superuser with full permissions."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)
    
    def user_exists(self, email):
        """Checks if a user with the specified email exists."""
        email = self.normalize_email(email)
        if self.model.objects.filter(email = email).exists():
            return True
        return False


class Profile(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model. Uses email as unique identifier.
    
    Inherits:AbstractBaseUser (handles password and login tracking)
        & PermissionsMixin (adds permission support).

    Attributes:
        email (EmailField): Unique email used for authentication.
        full_name (CharField): User's full name.
        is_active (bool): Account activation status.
        is_staff (bool): Admin site access status.
    """
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    avatar = models.URLField(blank=False, null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']     # for superuser
    
    objects = ProfileManager()
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        """Returns: first name (before space) or defaults to full name if no space."""
        return self.full_name.split()[0]
