from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('users.urls')),
    path('events/', include('events.urls')),
    path('tickets/', include('tickets.urls')),
    path('api/', include('api.urls')),
]
