from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('events/<int:event_id>/', views.event_tickets, name="event_tickets"),
    path('orders/', views.view_orders, name="view_orders"),
    path('orders/<int:order_id>/', views.order_tickets, name="order_tickets"),
]
