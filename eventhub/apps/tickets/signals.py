from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Ticket

@receiver(post_save, sender=Ticket)
def update_pricezone_on_ticket_save(sender, instance, created, **kwargs):
    """Update price zone's sold seats and revenue when a ticket is created."""
    if created:
        zone = instance.price_zone
        zone.seats_sold += 1
        zone.revenue += instance.price_zone.price
        zone.save(update_fields=['seats_sold', 'revenue'])
