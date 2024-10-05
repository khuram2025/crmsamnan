# crm/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

from accounts.models import Area
from .models import Customer
from .forms import CustomerForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Technician
from .forms import TechnicianForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Schedule, TechnicianSchedule, Slot
from .forms import ScheduleForm, TechnicianScheduleForm
from datetime import datetime, timedelta
CustomUser = get_user_model()

CustomUser = get_user_model()

def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.creation_method = 'AGENT'
            customer.save()
            
            if form.cleaned_data['create_account']:
                # Create a CustomUser for this customer
                password = CustomUser.objects.make_random_password()
                user = CustomUser.objects.create_user(
                    mobile=customer.mobile_number,
                    password=password
                )
                customer.user = user
                customer.save()
                messages.success(request, f'Customer added successfully. Their temporary password is: {password}')
            else:
                messages.success(request, 'Customer added successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'crm/customer_form.html', {'form': form})

@login_required
def schedule_list(request):
    schedules = Schedule.objects.all()
    return render(request, 'crm/schedule_list.html', {'schedules': schedules})

@login_required
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.created_by = request.user
            schedule.save()
            create_slots(schedule)
            messages.success(request, 'Schedule created successfully.')
            return redirect('schedule_list')
    else:
        form = ScheduleForm()
    return render(request, 'crm/schedule_form.html', {'form': form})

@login_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            schedule = form.save()
            schedule.slots.all().delete()  # Delete existing slots
            create_slots(schedule)  # Create new slots
            messages.success(request, 'Schedule updated successfully.')
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'crm/schedule_form.html', {'form': form, 'schedule': schedule})

@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully.')
        return redirect('schedule_list')
    return render(request, 'crm/schedule_confirm_delete.html', {'schedule': schedule})

@login_required
def technician_schedule_list(request):
    technician_schedules = TechnicianSchedule.objects.all()
    return render(request, 'crm/technician_schedule_list.html', {'technician_schedules': technician_schedules})

@login_required
def technician_schedule_create(request):
    if request.method == 'POST':
        form = TechnicianScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Technician schedule created successfully.')
            return redirect('technician_schedule_list')
    else:
        form = TechnicianScheduleForm()
    return render(request, 'crm/technician_schedule_form.html', {'form': form})

@login_required
def technician_schedule_edit(request, pk):
    technician_schedule = get_object_or_404(TechnicianSchedule, pk=pk)
    if request.method == 'POST':
        form = TechnicianScheduleForm(request.POST, instance=technician_schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Technician schedule updated successfully.')
            return redirect('technician_schedule_list')
    else:
        form = TechnicianScheduleForm(instance=technician_schedule)
    return render(request, 'crm/technician_schedule_form.html', {'form': form, 'technician_schedule': technician_schedule})

@login_required
def technician_schedule_delete(request, pk):
    technician_schedule = get_object_or_404(TechnicianSchedule, pk=pk)
    if request.method == 'POST':
        technician_schedule.delete()
        messages.success(request, 'Technician schedule deleted successfully.')
        return redirect('technician_schedule_list')
    return render(request, 'crm/technician_schedule_confirm_delete.html', {'technician_schedule': technician_schedule})

def create_slots(schedule):
    start_time = datetime.combine(datetime.today(), schedule.start_time)
    end_time = datetime.combine(datetime.today(), schedule.end_time)
    duration = schedule.get_duration()
    
    current_time = start_time
    while current_time + timedelta(minutes=duration) <= end_time:
        Slot.objects.create(
            schedule=schedule,
            start_time=current_time.time(),
            end_time=(current_time + timedelta(minutes=duration)).time()
        )
        current_time += timedelta(minutes=duration)

# crm/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Appointment, TechnicianSchedule, Slot
from .forms import AppointmentForm
import json
from django.core.serializers import serialize
from django.http import JsonResponse




@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('date', 'slot__start_time')
    return render(request, 'crm/appointment_list.html', {'appointments': appointments})

@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            mobile_number = form.cleaned_data['mobile_number']
            customer, created = Customer.objects.get_or_create(
                mobile_number=mobile_number,
                defaults={'name': name}
            )
            appointment = form.save(commit=False)
            appointment.customer = customer
            appointment.save()
            messages.success(request, 'Appointment booked successfully.')
            print(request, 'Appointment booked successfully.')
            return redirect('appointment_list')
        else:
            messages.error(request, 'There was an error with your form. Please check the details and try again.')
            print(request, 'There was an error with your form. Please check the details and try again.')
            print(form.errors)  # Add this line to print form errors to the console
    else:
        form = AppointmentForm()

    return render(request, 'crm/appointment_form.html', {'form': form})

@login_required
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully.')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'crm/appointment_form.html', {'form': form, 'appointment': appointment})

@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')
        return redirect('appointment_list')
    return render(request, 'crm/appointment_confirm_delete.html', {'appointment': appointment})

@login_required
def get_available_slots(request):
    technician_id = request.GET.get('technician')
    date = request.GET.get('date')

    if not technician_id or not date:
        return JsonResponse({'error': 'Both technician and date are required.'}, status=400)

    available_slots = Slot.objects.filter(
        technician_id=technician_id,
        date=date
    ).exclude(appointment__isnull=False)

    slots_data = [{'id': slot.id, 'time': f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"} 
                  for slot in available_slots]

    return JsonResponse({'slots': slots_data})

@login_required
def load_areas(request):
    city_id = request.GET.get('city_id')
    print(f"Received city_id: {city_id}")  # Debug log
    
    try:
        areas = Area.objects.filter(city_id=city_id)
        print(f"Found areas: {areas}")  # Debug log
        
        areas_data = json.loads(serialize('json', areas))
        areas_list = [{'id': area['pk'], 'name': area['fields']['name']} for area in areas_data]
        print(f"Sending areas data: {areas_list}")  # Debug log
        
        return JsonResponse(areas_list, safe=False)
    except Exception as e:
        print(f"Error in load_areas: {str(e)}")  # Debug log
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def load_technicians(request):
    area_id = request.GET.get('area_id')
    technicians = Technician.objects.filter(working_areas__id=area_id).values('id', 'name')
    return JsonResponse(list(technicians), safe=False)

@login_required
def load_slots(request):
    technician_id = request.GET.get('technician_id')
    date_str = request.GET.get('date')
    print(f"load_slots called with technician_id: {technician_id}, date: {date_str}")
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        print(f"Parsed date: {date}")
        slots = Slot.objects.filter(technician_id=technician_id, date=date, appointment__isnull=True).values('id', 'start_time', 'end_time')
        print(f"Found slots: {slots}")
        
        slots_list = list(slots)
        print(f"Sending slots data: {slots_list}")
        
        return JsonResponse(slots_list, safe=False)
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        print(f"Unexpected error in load_slots: {e}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

@login_required
def get_or_create_customer(request):
    name = request.GET.get('name')
    mobile = request.GET.get('mobile')
    customer, created = Customer.objects.get_or_create(mobile_number=mobile, defaults={'name': name})
    return JsonResponse({'id': customer.id, 'name': customer.name, 'mobile': customer.mobile_number})


from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import AddTeamMemberForm
from accounts.models import CustomUser

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def add_team_member(request):
    form = AddTeamMemberForm(request.POST)
    if form.is_valid():
        new_member = form.save(commit=False)
        new_member.team = request.user
        new_member.is_technician = (form.cleaned_data['user_type'] == 'TECHNICIAN')
        password = CustomUser.objects.make_random_password()
        new_member.set_password(password)
        new_member.save()
        
        # Create the associated Technician profile
        if new_member.is_technician:
            Technician.objects.create(user=new_member)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Team member added successfully. Their temporary password is: {password}'
        })
    else:
        return JsonResponse({'status': 'error', 'message': form.errors.as_json()})


