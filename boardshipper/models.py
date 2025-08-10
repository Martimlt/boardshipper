from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    business_name = models.CharField(max_length=200)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.business_name} - Profile"

class Booking(models.Model):
    # Link to user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    # Sender Information
    sender_name = models.CharField(max_length=200)
    
    # Recipient Information
    recipient_first_name = models.CharField(max_length=100)
    recipient_last_name = models.CharField(max_length=100)
    recipient_email = models.EmailField()
    recipient_phone = models.CharField(max_length=20)
    recipient_street = models.CharField(max_length=200)
    recipient_city = models.CharField(max_length=100)
    recipient_state = models.CharField(max_length=100)
    recipient_zip = models.CharField(max_length=20)
    recipient_country = models.CharField(max_length=100)
    
    # Package Details
    BOX_SIZE_CHOICES = [
        ('shortboard', 'Shortboard'),
        ('midlength', 'Midlength'),
        ('longboard', 'Longboard'),
    ]
    box_size = models.CharField(max_length=10, choices=BOX_SIZE_CHOICES)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    order_reference = models.CharField(max_length=100, blank=True)
    
    # Service Type
    SERVICE_CHOICES = [
        ('door-to-door', 'Door to Door'),
        ('airport-to-airport', 'Airport to Airport'),
    ]
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    
    # Additional Information
    additional_info = models.TextField(blank=True)
    
    # EasyPost Integration Fields
    label_url = models.URLField(blank=True, null=True)
    tracking_url = models.URLField(blank=True, null=True)
    easypost_shipment_id = models.CharField(max_length=100, blank=True, null=True)
    shipping_carrier = models.CharField(max_length=50, blank=True, null=True)
    shipping_service = models.CharField(max_length=100, blank=True, null=True)
    shipping_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Actual EasyPost rate
    shipping_rate_user = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Customer-facing rate
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_customer_price(self):
        """Calculate the price to show to the customer based on board size and destination"""
        is_california = self.recipient_state.upper() in ['CA', 'CALIFORNIA']
        
        if self.box_size == 'shortboard':
            return 55 if is_california else 75
        elif self.box_size == 'midlength':
            return 95 if is_california else 110
        elif self.box_size == 'longboard':
            return 155 if is_california else 175
        else:
            # Default to shortboard pricing if something goes wrong
            return 55 if is_california else 75
    
    def __str__(self):
        return f"{self.sender_name} - {self.recipient_first_name} {self.recipient_last_name} - {self.created_at.strftime('%Y-%m-%d')}"