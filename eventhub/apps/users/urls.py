from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('account/', views.account, name="account"),
    path('account/avatar/upload/', views.avatar_upload, name="avatar_upload"),
    path('account/avatar/delete/', views.avatar_delete, name="avatar_delete"),
    path('account/profile/', views.profile_update, name="profile_update"),
    path('logout/', views.logout, name="logout")
]