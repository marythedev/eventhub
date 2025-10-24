from django.db import models
from django.conf import settings

class Event(models.Model):
    """
    An event created by a user.

    Attributes:
        name (str): The name of the event, required.
        date (date): The scheduled date of the event, required.
        time (time): The scheduled start time of the event, required.
        location (str): The full address or location of the event, required.
        category (str): The category of the event, required.
        description (str): A detailed description of the event (max 5000 characters), optional.
        seating_type (str): Seating type of the event (general or reserved), required.
        organizer (Profile): The user who created the event.
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
    
    SEATING_TYPES = [
        ('general', 'General Admission'),
        ('reserved', 'Reserved Seating'),
    ]

    name = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField(blank=True)
    seating_type = models.CharField(max_length=10, choices=SEATING_TYPES)
    
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
    )
    
    def __str__(self):
        return self.name


class EventImage(models.Model):
    """
    An image for event.

    Attributes:
        event (Event): The event to which this image relates.
        image_url(str): The url by which the image can be accessed.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField()

    def __str__(self):
        return f"Image for {self.event.name}"


class EventPriceZone(models.Model):
    """
    A price zone (range of tickets selling for the same price) for the event.
    
    Attributes:
        event (Event): The event to which this price zone relates.
        zone_name (str): The name of the price zone.
        zone_price (float): The price of the price zone in USD.
        zone_seats (int): The capacity of seats of the price zone.
    """
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='price_zones'
    )
    zone_name = models.CharField(max_length=50)
    zone_price = models.DecimalField(max_digits=8, decimal_places=2)
    zone_seats = models.PositiveBigIntegerField()

    def __str__(self):
        return f"Price Zone {self.zone_name} for {self.event.name} event"
