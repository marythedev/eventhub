from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Ticket, TicketInProcess


@receiver(post_save, sender=Ticket)
def update_pricezone_on_ticket_save(sender, instance, created, **kwargs):       # pylint: disable=unused-argument
    """Update price zone's sold seats and revenue when a Ticket is created."""
    if created:
        zone = instance.price_zone
        zone.seats_sold += 1
        zone.revenue += instance.price_zone.price
        zone.save(update_fields=['seats_sold', 'revenue'])

@receiver(post_save, sender=TicketInProcess)
def update_seats_reserved_on_save(sender, instance, created, **kwargs):     # pylint: disable=unused-argument
    """Update price zone's reserved seats after a TicketInProcess is created."""
    if created:
        price_zone = instance.price_zone
        price_zone.seats_reserved += 1
        price_zone.save()

@receiver(post_delete, sender=TicketInProcess)
def update_seats_reserved_on_delete(sender, instance, **kwargs):        # pylint: disable=unused-argument
    """Update price zone's reserved seats after a TicketInProcess is deleted."""
    price_zone = instance.price_zone
    price_zone.seats_reserved -= 1
    price_zone.save()
