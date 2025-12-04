from django.utils import timezone
from events.models import Event

from .models import Ticket


def validate_ticket(ticket_number, event_id, user):     # pylint: disable=too-many-return-statements
    """
    Validate tickets for the event.
    
    Args:
        "ticket_number": number of the ticket to be validated (format: EH-TCK-<YEAR>-<TICKET-ID>)
        "event_id": event ID for which ticket is being validated
        "user": user, who is attempting to validate the ticket
    
    Validation Rules:
        - Ticket number and event ID should be provided.
        - Event with given event ID must exist.
        - User, who validates the ticket must be either event organizer or part of event team.
        - Ticket must exist for this event.
        - If event does not allow re-entry, ticket must not be previously validated.
    
    If validation rules were passed, validate the ticket by updating 'validated_at' field with current datetime.

    Returns: a dictionary with ticket validation information
        {
            "valid: True/False,                 # indicates whether validation was successful or not
            "status": status code,              # "error", "not_found", "forbidden" or "used"
            "message": explanation message      # short explanation of the result
        }
    """

    # check if required parameters are provided
    if not ticket_number:
        return {"valid": False, "status": "error", "message": "Ticket Number is not provided."}
    if not event_id:
        return {"valid": False, "status": "error", "message": "Event ID is not provided."}


    # check if event is valid
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return {"valid": False, "status": "not_found", "message": "Event does not exist."}
    except Exception:       # pylint: disable=broad-exception-caught
        return {"valid": False, "status": "error", "message": "Invalid event ID."}


    # check if user is allowed to validate tickets for this event
    if not (event.organizer == user or event.is_team_member(user)):
        return {"valid": False, "status": "forbidden",
                "message": "You do not have permission to validate tickets for this event."}


    # check if ticket exists for this event
    try:
        ticket = Ticket.objects.get(number=ticket_number, price_zone__event_id=event_id)
    except Ticket.DoesNotExist:
        return {"valid": False, "status": "not_found", "message": "Ticket does not exist."}


    # check if ticket has not been previously validated or if event allows re-entry
    if ticket.validated_at and not event.allow_reentry:
        return {"valid": False, "status": "used", "message": "Ticket already used. Re-entry not allowed."}


    # validate ticket
    ticket.validated_at = timezone.now()
    ticket.save(update_fields=["validated_at"])

    return {
        "valid": True,
        "status": "valid",
        "message": "Ticket is valid."
    }
