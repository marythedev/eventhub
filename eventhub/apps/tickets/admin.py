from django.contrib import admin

from .models import Ticket, TicketInProcess

admin.site.register(Ticket)
admin.site.register(TicketInProcess)
