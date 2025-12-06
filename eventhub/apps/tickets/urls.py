from django.urls import path

from . import views

app_name = 'tickets'

urlpatterns = [
    path('events/', views.upcoming_events, name="upcoming_events"),
    path('events/<int:event_id>/', views.event_tickets, name="event_tickets"),
    path('validate/<int:event_id>/', views.validate_tickets, name="validate_tickets"),
    path('orders/', views.view_orders, name="view_orders"),
    path('orders/<str:order_number>/', views.order_tickets, name="order_tickets"),
]
