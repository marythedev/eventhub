from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('explore/', views.view_events, name="view_events"),
    path('create/', views.create_event, name="create_event"),
    path('view/<int:event_id>/', views.view_event, name="view_event")
]
