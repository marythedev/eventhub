from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('explore/', views.view_events, name="view_events"),
    path('create/', views.create_event, name="create_event"),
    path('view/<int:event_id>/', views.view_event, name="view_event"),
    path('checkout/<int:event_id>/', views.checkout, name="checkout"),
    path('checkout/<int:event_id>/success', views.payment_success, name="payment_success"),
    path('checkout/<int:event_id>/fail', views.payment_fail, name="payment_fail")
]
