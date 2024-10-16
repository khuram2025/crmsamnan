# accounts/views.py

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import City, Area, Service
from crmapp.models import Appointment, Technician, Customer

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')  # Redirect to profile after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def test_page(request):
    print(f"Rendering template with static files. STATIC_URL: {settings.STATIC_URL}")
    return render(request, 'account/login.html')

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            mobile = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=mobile, password=password)
            if user is not None:
                login(request, user)
                print(request, f"Welcome back, {mobile}!")
                return redirect('profile')  # Redirect to profile after login
            else:
                print(request, "Invalid mobile number or password.")
        else:
            print(request, "Invalid mobile number or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    team_members = []
    appointments = []
    
    if user.user_type == 'MANAGER':
        team_members = user.get_technicians()
        # Get appointments for all technicians under this manager
        technician_users = Technician.objects.filter(user__in=team_members)
        appointments = Appointment.objects.select_related(
            'slot__technician', 
            'customer', 
            'slot__technician__user',
            'customer__user'
        ).filter(slot__technician__in=technician_users).order_by('slot__date', 'slot__start_time')
    elif user.is_technician:
        team_members = user.get_managers()
        # Get appointments for this technician
        technician = Technician.objects.get(user=user)
        appointments = Appointment.objects.select_related(
            'slot__technician', 
            'customer', 
            'slot__technician__user',
            'customer__user'
        ).filter(slot__technician=technician).order_by('slot__date', 'slot__start_time')
    else:
        # For customers or other user types
        appointments = Appointment.objects.select_related(
            'slot__technician', 
            'customer', 
            'slot__technician__user',
            'customer__user'
        ).filter(customer=user).order_by('slot__date', 'slot__start_time')
    
    context = {
        'user': user,
        'team_members': team_members,
        'appointments': appointments,
        'appointment_count': appointments.count(),
    }
    return render(request, 'account/profile.html', context)
@login_required
def appointment_booking(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            appointment.save()
            return redirect('appointment_confirmation')
    else:
        form = AppointmentForm()

    cities = City.objects.all()
    services = Service.objects.all()

    return render(request, 'account/appointment_booking.html', {
        'form': form,
        'cities': cities,
        'services': services,
    })

from django.http import JsonResponse
from django.shortcuts import render
from .models import Area

def get_areas(request):
    city_id = request.GET.get('city_id')
    areas = Area.objects.filter(city_id=city_id).values('id', 'name')
    return JsonResponse(list(areas), safe=False)