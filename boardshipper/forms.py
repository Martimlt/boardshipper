from django import forms
from .models import Booking

# Common country choices for surfboard shipping
COUNTRY_CHOICES = [
    ('', 'Select Country'),
    ('United States', 'United States'),
    ('Canada', 'Canada'),
    ('Mexico', 'Mexico'),
    ('Australia', 'Australia'),
    ('New Zealand', 'New Zealand'),
    ('United Kingdom', 'United Kingdom'),
    ('France', 'France'),
    ('Spain', 'Spain'),
    ('Portugal', 'Portugal'),
    ('Brazil', 'Brazil'),
    ('Argentina', 'Argentina'),
    ('Chile', 'Chile'),
    ('Peru', 'Peru'),
    ('Ecuador', 'Ecuador'),
    ('Costa Rica', 'Costa Rica'),
    ('Panama', 'Panama'),
    ('Nicaragua', 'Nicaragua'),
    ('El Salvador', 'El Salvador'),
    ('Guatemala', 'Guatemala'),
    ('Japan', 'Japan'),
    ('Indonesia', 'Indonesia'),
    ('Philippines', 'Philippines'),
    ('Thailand', 'Thailand'),
    ('Malaysia', 'Malaysia'),
    ('Singapore', 'Singapore'),
    ('South Africa', 'South Africa'),
    ('Morocco', 'Morocco'),
    ('Ireland', 'Ireland'),
    ('Germany', 'Germany'),
    ('Italy', 'Italy'),
    ('Netherlands', 'Netherlands'),
    ('Belgium', 'Belgium'),
    ('Switzerland', 'Switzerland'),
    ('Austria', 'Austria'),
    ('Norway', 'Norway'),
    ('Sweden', 'Sweden'),
    ('Denmark', 'Denmark'),
    ('Finland', 'Finland'),
]

class BookingForm(forms.ModelForm):
    recipient_country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_country'}),
        label='Country *'
    )
    class Meta:
        model = Booking
        exclude = ['user', 'sender_name', 'label_url', 'tracking_url', 'easypost_shipment_id', 'service']
        labels = {
            'recipient_first_name': 'First Name *',
            'recipient_last_name': 'Last Name *',
            'recipient_email': 'Email *',
            'recipient_phone': 'Phone Number *',
            'recipient_street': 'Street Address *',
            'recipient_city': 'City *',
            'recipient_state': 'State/Province *',
            'recipient_zip': 'Zip/Postal Code *',
            'box_size': 'Board Type *',
            'weight': 'Weight (lbs) *',
            'order_reference': 'Order Reference',
            'additional_info': 'Additional Information',
        }
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_sender_name'}),
            'recipient_first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_first_name'}),
            'recipient_last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_last_name'}),
            'recipient_email': forms.EmailInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_email', 'placeholder': 'recipient@example.com'}),
            'recipient_phone': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_phone', 'placeholder': '(555) 123-4567'}),
            'recipient_street': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_street'}),
            'recipient_city': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_city'}),
            'recipient_state': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_state'}),
            'recipient_zip': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'id': 'id_recipient_zip'}),
            'box_size': forms.Select(attrs={'class': 'form-control', 'required': True, 'id': 'id_box_size'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'required': True, 'id': 'id_weight'}),
            'order_reference': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_order_reference'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any special instructions or requirements...', 'id': 'id_additional_info'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        box_size = cleaned_data.get('box_size')
        recipient_state = cleaned_data.get('recipient_state')
        recipient_country = cleaned_data.get('recipient_country')
        
        # Only allow US shipping
        if recipient_country and recipient_country != 'United States':
            raise forms.ValidationError(
                'Shipping is currently only available within the United States. '
                'For international shipping, please contact support.'
            )
        
        # ONLY allow shipping to these specific states
        allowed_states = [
            'CA', 'CALIFORNIA', 
            'OR', 'OREGON', 
            'WA', 'WASHINGTON',
            'CO', 'COLORADO', 
            'ID', 'IDAHO', 
            'AZ', 'ARIZONA'
        ]
        
        if recipient_state and recipient_state.upper() not in allowed_states:
            raise forms.ValidationError(
                'We are unable to ship to this location. Please contact support for assistance.'
            )
        
        # Check longboard restrictions
        if box_size == 'longboard' and recipient_state:
            longboard_states = ['CA', 'CALIFORNIA', 'OR', 'OREGON', 'WA', 'WASHINGTON', 
                              'CO', 'COLORADO', 'ID', 'IDAHO', 'AZ', 'ARIZONA']
            if recipient_state.upper() not in longboard_states:
                raise forms.ValidationError(
                    'Longboard shipping is only available to CA, OR, WA, CO, ID, and AZ. '
                    'Please select Shortboard or Midlength for other states.'
                )
        
        return cleaned_data