from django.contrib import admin
from .models import *

admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(EventPriceZone)
admin.site.register(Order)
admin.site.register(Ticket)