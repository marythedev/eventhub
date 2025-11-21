from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('explore/', views.view_events, name="view_events"),
    path('create/', views.create_event, name="create_event"),
    path('edit/<int:event_id>/', views.edit_event, name="edit_event"),
    path('<int:event_id>/', views.view_event, name="view_event"),
    path('<int:event_id>/checkout/', views.checkout, name="checkout"),
    
    # TODO move from order id to slug:order_number in url for better comprehensiveness on checkout
    path('<int:event_id>/checkout/success/<int:order_id>', views.checkout_success, name="checkout_success"),
    path('<int:event_id>/checkout/fail/<int:order_id>', views.checkout_fail, name="checkout_fail"),
    
    # user-owned events
    path('my-events/', views.my_events, name="my_events"),
    # TODO edit event
]
