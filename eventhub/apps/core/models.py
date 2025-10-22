from django.db import models
from django.conf import settings

class Event(models.Model):
    """
    An event created by a user.

    Attributes:
        event_name (str): The name of the event, required.
        event_date (date): The scheduled date of the event, required.
        event_time (time): The scheduled start time of the event, required.
        event_location (str): The full address or location of the event, required.
        event_category (str): The category of the event, required.
        event_description (str): A detailed description of the event (max 5000 characters), optional.
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

    event_name = models.CharField(max_length=200)
    event_date = models.DateField()
    event_time = models.TimeField()
    event_location = models.CharField(max_length=255)
    event_category = models.CharField(max_length=20, choices=CATEGORIES)
    event_description = models.TextField(blank=True)
    
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
    )
    
    def __str__(self):
        return self.event_name
