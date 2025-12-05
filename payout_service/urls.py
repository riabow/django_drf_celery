"""
URL configuration for payout_service project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('payouts.urls')),
    # Встроенная авторизация DRF для browsable API (логин/логаут).
    path('api-auth/', include('rest_framework.urls')),
]

