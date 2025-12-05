from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Event(models.Model):
    """
    An event created by a user.

    Attributes:
        name (str): The name of the event, required.
        date (datetime): The scheduled date and time of the event, required.
        location (str): The full address or location of the event, required.
        location_lat (float): Location latitude value, required.
        location_lon (float): Location longitude value, required.
        category (str): The category of the event, required.
        description (str): A detailed description of the event (max 5000 characters), optional.
        organizer (Profile): The user who created the event.
        team (Profile - ManyToMany): Additional users assigned to the event team.
            These users are able to validate (scan) tickets for the event.
        allow_reentry (bool): States whether attendees can leave and re-enter this event.
    """

    CATEGORIES = [
        ('arts', 'Arts'),
        ('business', 'Business'),
        ('family', 'Family'),
        ('food', 'Food & Drink'),
        ('music', 'Music & Concerts'),
        ('social', 'Social & Comedy'),
        ('sports', 'Sports'),
        ('tech', 'Technology'),
    ]

    ICONS = {
        'arts': 'fa-film',
        'business': 'fa-briefcase',
        'family': 'fa-heart',
        'food': 'fa-martini-glass-citrus',
        'music': 'fa-music',
        'social': 'fa-comments',
        'sports': 'fa-basketball',
        'tech': 'fa-code',
    }

    name = models.CharField(max_length=50)
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField(blank=True)
    allow_reentry = models.BooleanField(default=False)

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
    )

    team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='team_events',
        blank=True,
        help_text="Users allowed to validate (scan) tickets for this event."
    )

    def __str__(self):
        return self.name

    def is_team_member(self, user):
        """Return True if the user is a member of the event's team."""
        return self.team.filter(id=user.id).exists()

    @property
    def category_label(self):
        """Returns the full category name."""
        return dict(self.CATEGORIES).get(self.category, self.category)

    @property
    def category_icon(self):
        """Returns icon for the category."""
        return self.ICONS.get(self.category, 'fa-tag')

    @property
    def is_past(self):
        """Returns True if event date is in the past."""
        return self.date < timezone.now()

    @property
    def days_until(self):
        """Return the number of days until the event date (negative for past events)."""
        now = timezone.localtime().date()
        event_day = timezone.localtime(self.date).date()
        return (event_day - now).days

    @property
    def total_seats(self):
        """Return the total number of seats across all price zones."""
        total_seats = 0
        for zone in self.price_zones.all():
            total_seats += zone.seats
        return total_seats

    @property
    def total_seats_sold(self):
        """Return the total number of sold seats across all price zones."""
        total_seats_sold = 0
        for zone in self.price_zones.all():
            total_seats_sold += zone.seats_sold
        return total_seats_sold

    @property
    def revenue(self):
        """Return the total revenue generated across all price zones."""
        revenue = 0
        for zone in self.price_zones.all():
            revenue += zone.revenue
        return revenue


class EventImage(models.Model):
    """
    An image for event.

    Attributes:
        event (Event): The event to which this image relates.
        url(str): The url by which the image can be accessed.
    """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='images'
    )
    url = models.URLField()

    def __str__(self):
        return f"Image for {self.event.name}"


class EventPriceZone(models.Model):
    """
    A price zone (range of tickets selling for the same price) for the event.

    Attributes:
        event (Event): The event to which this price zone relates.
        name (str): The name of the price zone.
        desc (str): Brief description of the price zone.
        price (float): The price of the price zone in USD.
        seats (int): The total capacity of seats of the price zone.
        seats_sold (int): The number of seats already sold.
        seats_reserved (int): The number of seats that have been reserved but not yet paid for.
        revenue (Decimal): The total revenue generated from tickets sold in this price zone.
    """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='price_zones'
    )
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    seats = models.PositiveBigIntegerField()
    seats_sold = models.PositiveIntegerField(default=0)
    seats_reserved = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def __str__(self):
        return f"Price Zone {self.name} for {self.event.name} event"

    @property
    def remaining_seats(self):
        """Return the number of seats (tickets) available for sale in this price zone."""
        return self.seats - self.seats_sold - self.seats_reserved
