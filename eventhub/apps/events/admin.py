from django.contrib import admin
from .models import Event, EventImage, EventPriceZone, Order

admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(EventPriceZone)
admin.site.register(Order)
