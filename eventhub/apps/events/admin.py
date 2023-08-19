from django.contrib import admin

from .models import User, Seat, Concert, Payment, Ticket, Order

admin.site.register(User)
admin.site.register(Concert)
admin.site.register(Seat)
admin.site.register(Payment)
admin.site.register(Ticket)
admin.site.register(Order)