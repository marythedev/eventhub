from django.contrib import admin

from .models import Event, EventAdmin, EventImage, EventPriceZone

admin.site.register(Event, EventAdmin)
admin.site.register(EventImage)
admin.site.register(EventPriceZone)
