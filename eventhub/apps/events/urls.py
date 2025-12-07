from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('explore/', views.view_events, name="view_events"),
    path('my-events/', views.my_events, name="my_events"),
    path('create/', views.create_event, name="create_event"),
    path('edit/<int:event_id>/', views.edit_event, name="edit_event"),
    path('delete/<int:event_id>/', views.delete_event, name="delete_event"),
    path('<int:event_id>/', views.view_event, name="view_event"),
    path('<int:event_id>/team/add/', views.add_team_member, name='add_team_member'),
    path('<int:event_id>/team/remove/', views.remove_team_member, name='remove_team_member'),
]
