from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name = "home"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('account/', views.account, name="account"),
    path('events/', views.events, name="events"),
    path('purchase/', views.purchase, name='purchase'),
    path('payment/', views.pay, name='pay'),
    path('orders/', views.orders, name="orders")
]