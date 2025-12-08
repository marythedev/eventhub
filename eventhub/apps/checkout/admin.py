from django.contrib import admin

from .models import Order


class OrderAdmin(admin.ModelAdmin):
    """Display order's date field on admin."""
    readonly_fields = ("date",)

admin.site.register(Order, OrderAdmin)
