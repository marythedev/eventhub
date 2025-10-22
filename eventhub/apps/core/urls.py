from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name="home"),
    path('explore/', views.explore, name="explore"),
    path('event/create/', views.create_event, name="create_event")
]
