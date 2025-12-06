from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from events.models import EventPriceZone

from .models import Ticket, TicketInProcess


@receiver(post_save, sender=Ticket)
def update_pricezone_on_ticket_save(sender, instance, created, **kwargs):       # pylint: disable=unused-argument
    """Update price zone's sold seats and revenue when a Ticket is created."""
    if created:
        price_zone = instance.price_zone
        EventPriceZone.objects.filter(pk=price_zone.pk).update(
            seats_sold=F('seats_sold') + 1,
            revenue=F('revenue') + F('price')
        )


@receiver(post_save, sender=TicketInProcess)
def update_seats_reserved_on_save(sender, instance, created, **kwargs):     # pylint: disable=unused-argument
    """Update price zone's reserved seats after a TicketInProcess is created."""
    if created:
        price_zone = instance.price_zone
        EventPriceZone.objects.filter(pk=price_zone.pk).update(
            seats_reserved=F('seats_reserved') + 1
        )

@receiver(post_delete, sender=TicketInProcess)
def update_seats_reserved_on_delete(sender, instance, **kwargs):        # pylint: disable=unused-argument
    """Update price zone's reserved seats after a TicketInProcess is deleted."""
    price_zone = instance.price_zone
    EventPriceZone.objects.filter(pk=price_zone.pk).update(
        seats_reserved=F('seats_reserved') - 1
    )
