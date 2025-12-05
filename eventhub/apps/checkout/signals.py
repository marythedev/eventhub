from checkout.models import Order
from django.db.models.signals import post_save
from django.dispatch import receiver
from tickets.models import TicketInProcess

from .utils import save_tickets


@receiver(post_save, sender=Order)
def handle_order_status_update(sender, instance, created, **kwargs):    # pylint: disable=unused-argument
    """
    When the Order status is changed to 'succeeded', 
    convert all TicketInProcess objects for that order to Ticket objects.
    """
    if instance.status == "succeeded":
        tickets_in_process = TicketInProcess.objects.filter(order=instance)
        save_tickets(tickets=tickets_in_process, order=instance)
        tickets_in_process = TicketInProcess.objects.filter(order=instance)
