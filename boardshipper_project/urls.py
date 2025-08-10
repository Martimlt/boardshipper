"""
URL configuration for boardshipper_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('boardshipper.urls')),
]

# Custom error handlers
handler404 = 'boardshipper.views.custom_404'
handler500 = 'boardshipper.views.custom_500'