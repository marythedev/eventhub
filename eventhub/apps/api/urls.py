from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path("barcode/<int:ticket_id>/", views.ticket_barcode, name="ticket_barcode"),
    # TODO POST /api/validate-ticket
]