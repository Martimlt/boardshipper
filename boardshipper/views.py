from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Booking, UserProfile
from .forms import BookingForm
from .auth_forms import LoginForm, RegistrationForm

def home(request):
    return render(request, 'home.html')

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
            messages.success(request, 'Thank you for your booking request! We will process your information and contact you soon with shipping details.')
            return redirect('home')
    else:
        form = BookingForm()
    
    return render(request, 'book_django.html', {'form': form})