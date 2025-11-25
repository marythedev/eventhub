from django.contrib import admin

from .models import Profile, StripeAccount

admin.site.register(Profile)
admin.site.register(StripeAccount)
