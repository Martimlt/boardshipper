from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Booking, UserProfile
from .forms import BookingForm
from .auth_forms import LoginForm, RegistrationForm
from .utils import create_easypost_shipment

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('book')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                # Set a flag to show welcome message
                request.session['just_logged_in'] = True
                next_page = request.GET.get('next', 'book')
                return redirect(next_page)
            else:
                form.add_error('password', 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('book')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            business_name = form.cleaned_data['business_name']
            # Removed success message
            return redirect('book')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    # Removed logout success message
    return redirect('home')

@login_required
def book(request):
    # Check if user just logged in
    show_welcome = request.session.pop('just_logged_in', False)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.service = 'door-to-door'

            if hasattr(request.user, 'profile'):
                booking.sender_name = request.user.profile.business_name
            else:
                booking.sender_name = request.user.first_name
            booking.save()
            
            try:
                if hasattr(request.user, 'profile'):
                    sender_profile = request.user.profile
                    result = create_easypost_shipment(sender_profile, booking)
                    booking.label_url = result['label_url']
                    booking.tracking_url = result['tracking_url']
                    booking.easypost_shipment_id = result['shipment_id']
                    booking.shipping_carrier = result.get('carrier', '')
                    booking.shipping_service = result.get('service', '')
                    # Store both the actual EasyPost rate and customer price
                    booking.shipping_rate = result.get('rate', 0)  # Actual EasyPost rate
                    booking.shipping_rate_user = booking.get_customer_price()  # Customer-facing price
                    booking.save()
            except Exception:
                pass
            
            return redirect('booking_detail', pk=booking.pk)
        else:
            # Don't add message here since form errors are already displayed
            pass
    else:
        form = BookingForm()
    
    return render(request, 'book.html', {'form': form, 'show_welcome': show_welcome})

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'booking_detail.html', {'booking': booking})

@login_required
def shipments(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shipments.html', {'bookings': bookings})

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)