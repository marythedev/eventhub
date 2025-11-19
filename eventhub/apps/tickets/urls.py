from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('orders/', views.view_orders, name="view_orders"),
    path('orders/<int:order_id>/', views.order_tickets, name="order_tickets"),
]
