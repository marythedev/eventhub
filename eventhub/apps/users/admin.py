from django.contrib import admin

from .models import Profile, ProfileAdmin, StripeAccount

admin.site.register(Profile, ProfileAdmin)
admin.site.register(StripeAccount)
