from django.contrib import admin

from .models import Event, EventImage, EventPriceZone


class EventAdmin(admin.ModelAdmin):
    """Overrides bulk delete in admin to use custom delete logic for events."""

    def delete_queryset(self, request, queryset):
        for event in queryset:
            event.delete()

admin.site.register(Event, EventAdmin)
admin.site.register(EventImage)
admin.site.register(EventPriceZone)
