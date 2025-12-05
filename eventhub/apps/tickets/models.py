from checkout.models import Order
from django.conf import settings
from django.db import models
from django.utils import timezone
from events.models import EventPriceZone


class Ticket(models.Model):
    """
    Ticket that was purchased.

    Attributes:
        number (str): Unique ticket identifier (auto generated).
        price_zone (EventPriceZone): EventPriceZone which ticket is associated with.
        order (Order): Order in which ticket was purchased.
        validated_at (datetime): Timestamp when the ticket was last validated.
    """

    number = models.CharField(max_length=50, unique=True, blank=False)
    price_zone = models.ForeignKey(
        EventPriceZone,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    validated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Ticket {self.number} owned by {self.order.acquirer}"

    def save(self, *args, **kwargs):
        """
        Overridden save method.
        Auto generates unique ticket number (EH-TCK-YEAR-ID) on initial save.
        """

        initial = self.pk is None
        super().save(*args, **kwargs)

        if initial:
            year = timezone.now().year
            self.number = f"EH-TCK-{year}-{self.id}"
            super().save(update_fields=['number'])


class TicketInProcess(models.Model):
    """
    Ticket that was selected but not purchased yet.

    TicketInProcess represents a reservation for the ticket during checkout. 
    Once the order is successful, Ticket objects are created based off TicketInProcess objects information.
        TicketInProcess objects is deleted. If order is unsuccessful, TicketInProcess objects are deleted.
        If order was not made within a period of time (i.e. 10 mins), ticket in process are 
        released (deleted) for other people to buy.

    Attributes:
        price_zone (EventPriceZone): EventPriceZone which ticket is associated with.
        order (Order): Order in which ticket is being purchased, not required.
        reserver (Profile): User who has selected the ticket.
        reserved_at (datetime): Date and time when the order was selected.
    """

    price_zone = models.ForeignKey(
        EventPriceZone,
        on_delete=models.CASCADE,
        related_name='tickets_in_process'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tickets_in_process',
        blank=True,
        null=True
    )
    reserver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets_in_process'
    )
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id} reserved by {self.reserver} (non-purchased ticket)"
