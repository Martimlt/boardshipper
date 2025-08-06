from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'recipient_first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'recipient_last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'recipient_street': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'recipient_city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'recipient_state': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'recipient_zip': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'recipient_country': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'box_size': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'required': True}),
            'order_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'service': forms.RadioSelect(),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any special instructions or requirements...'}),
        }