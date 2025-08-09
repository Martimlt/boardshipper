from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('book/', views.book, name='book'),
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('shipments/', views.shipments, name='shipments'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]