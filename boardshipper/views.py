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
            
            # Try to authenticate with email as username
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                # Get business name from profile
                business_name = user.profile.business_name if hasattr(user, 'profile') else user.first_name
                messages.success(request, f'Welcome back, {business_name}!')
                # Redirect to booking page after login
                next_page = request.GET.get('next', 'book')
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid email or password.')
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
            messages.success(request, f'Welcome to BoardShipper, {business_name}!')
            return redirect('book')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def book(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # Pre-fill sender name from business profile
            if hasattr(request.user, 'profile'):
                booking.sender_name = request.user.profile.business_name
            else:
                booking.sender_name = request.user.first_name
            booking.save()
            
            # === CREATE LABEL WITH EASYPOST ===
            try:
                if hasattr(request.user, 'profile'):
                    sender_profile = request.user.profile
                    result = create_easypost_shipment(sender_profile, booking)
                    booking.label_url = result['label_url']
                    booking.tracking_url = result['tracking_url']
                    booking.easypost_shipment_id = result['shipment_id']
                    booking.save()
                    messages.success(request, 'Booking successful! Your shipping label has been created. You can download or print your label below.')
                else:
                    messages.warning(request, 'Booking saved but label creation requires a complete business profile.')
            except Exception as e:
                messages.warning(request, f'Booking saved but label creation failed: {str(e)}. We will contact you with shipping details.')
            
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm()
    
    return render(request, 'book_django.html', {'form': form})

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'booking_detail.html', {'booking': booking})