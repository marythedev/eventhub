from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path("barcode/<int:ticket_id>/", views.ticket_barcode, name="ticket_barcode"),
    # TODO display date in local time
    path('orders/<int:order_id>/receipt/', views.order_receipt, name='order_receipt'),
    # TODO POST /api/validate-ticket
]