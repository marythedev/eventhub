from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path("barcode/<int:ticket_id>/", views.ticket_barcode, name="ticket_barcode"),
    path('orders/<int:order_id>/receipt/', views.order_receipt, name='order_receipt'),
    # TODO POST /api/validate-ticket
    
    path('stripe/setup', views.stripe_setup, name="stripe_setup"),
    path('stripe/delete', views.stripe_delete, name="stripe_delete"),
]