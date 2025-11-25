from django.db import models
from django.utils import timezone

from events.models import EventPriceZone, Order


class Ticket(models.Model):
    """
    Ticket that was purchased.

    Attributes:
        number (str): Unique ticket identifier (auto generated).
        price_zone (EventPriceZone): EventPriceZone which ticket is associated with.
        order (Order): Order in which ticket was purchased.
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
