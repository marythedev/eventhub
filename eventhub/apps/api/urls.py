from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path("search/all/", views.search_all, name="search_all"),
    path("search/my-events/", views.search_my_events, name="search_my_events"),
    path("search/my-orders/", views.search_events_from_orders, name="search_events_from_orders"),
    path("barcode/<int:ticket_id>/", views.ticket_barcode, name="ticket_barcode"),
    path('orders/<int:order_id>/receipt/', views.order_receipt, name='order_receipt'),
    # TODO POST /api/validate-ticket

    path('stripe/setup', views.stripe_setup, name="stripe_setup"),
    path('stripe/delete', views.stripe_delete, name="stripe_delete"),
]
