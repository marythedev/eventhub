from django.contrib import admin

from .models import Profile, StripeAccount


class ProfileAdmin(admin.ModelAdmin):
    """Overrides bulk delete in admin to use custom delete logic for user profiles."""

    def delete_queryset(self, request, queryset):
        for profile in queryset:
            profile.delete()

admin.site.register(Profile, ProfileAdmin)
admin.site.register(StripeAccount)
