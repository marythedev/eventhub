from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from tickets.models import TicketInProcess

RESERVED_TICKET_EXPIRATION_MIN = settings.RESERVED_TICKET_EXPIRATION_MIN

class Command(BaseCommand):
    """
    Release non-purchased reserved tickets after some time to allow other people buy them.
    Made for periodic runs.
    
    Command:
        python manage.py cleanup_expired_tickets

    Behavior:
        Deletes TicketInProcess records that:
        - Are not associated with any order (purchase attempt not made).
        - Were reserved more than RESERVED_TICKET_EXPIRATION_MIN minutes ago.
    """

    help = "Cleanup reserved tickets that were not purchased."

    def handle(self, *args, **options):
        expiration_time = timezone.now() - timedelta(minutes=RESERVED_TICKET_EXPIRATION_MIN)
        TicketInProcess.objects.filter(
            reserved_at__lte=expiration_time,
            order__isnull=True
        ).delete()
