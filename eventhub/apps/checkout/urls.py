from django.urls import path

from . import views

app_name = 'checkout'

urlpatterns = [
    path('<int:event_id>/', views.checkout, name="checkout"),
    path('<int:event_id>/action-required/<str:order_number>/', views.action_required, name="action_required"),
    path('<int:event_id>/success/<str:order_number>/', views.success, name="success"),
    path('<int:event_id>/fail/<str:order_number>/', views.fail, name="fail"),
]
