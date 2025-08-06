from django.contrib import admin
from .models import Booking, UserProfile

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'sender_name', 'recipient_first_name', 'recipient_last_name', 'box_size', 'service', 'created_at']
    list_filter = ['box_size', 'service', 'created_at']
    search_fields = ['sender_name', 'recipient_first_name', 'recipient_last_name', 'order_reference', 'user__email']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'city', 'state', 'country']
    search_fields = ['business_name', 'user__email', 'city', 'state']
    list_filter = ['country', 'state']