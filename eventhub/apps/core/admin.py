from django.contrib import admin

from .models import ContactInquiry


class ContactInquiryAdmin(admin.ModelAdmin):
    """Display contact inquiry's date field on admin."""
    readonly_fields = ("date",)

admin.site.register(ContactInquiry, ContactInquiryAdmin)
