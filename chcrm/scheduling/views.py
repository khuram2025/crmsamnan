from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Shift, WorkingSlot, TechnicianAvailability
from .forms import ShiftForm, WorkingSlotForm, TechnicianAvailabilityForm
from profiles.models import TechnicianProfile
from datetime import datetime, timedelta

def is_admin_or_manager(user):
    return user.is_authenticated and user.role in ['ADMIN', 'MANAGER']

# Shift views
@login_required
@user_passes_test(is_admin_or_manager)
def shift_list(request):
    shifts = Shift.objects.all()
    return render(request, 'scheduling/shift_list.html', {'shifts': shifts})

@login_required
@user_passes_test(is_admin_or_manager)
def shift_create(request):
    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift created successfully.')
            return redirect('shift_list')
    else:
        form = ShiftForm()
    return render(request, 'scheduling/shift_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def shift_edit(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == 'POST':
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift updated successfully.')
            return redirect('shift_list')
    else:
        form = ShiftForm(instance=shift)
    return render(request, 'scheduling/shift_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def shift_delete(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == 'POST':
        shift.delete()
        messages.success(request, 'Shift deleted successfully.')
        return redirect('shift_list')
    return render(request, 'scheduling/shift_confirm_delete.html', {'shift': shift})

# WorkingSlot views
@login_required
@user_passes_test(is_admin_or_manager)
def working_slot_list(request):
    working_slots = WorkingSlot.objects.all()
    return render(request, 'scheduling/working_slot_list.html', {'working_slots': working_slots})

@login_required
@user_passes_test(is_admin_or_manager)
def working_slot_create(request):
    if request.method == 'POST':
        form = WorkingSlotForm(request.POST)
        if form.is_valid():
            shift = form.cleaned_data['shift']
            duration = form.cleaned_data['duration']
            gap = form.cleaned_data['gap_between_slots'] or timedelta(minutes=0)

            # Create slots automatically
            slots = WorkingSlot.create_slots(shift=shift, duration=duration, gap=gap)
            
            # Bulk create slots
            WorkingSlot.objects.bulk_create(slots)

            messages.success(request, 'Working slots created successfully.')
            return redirect('working_slot_list')
    else:
        form = WorkingSlotForm()
    return render(request, 'scheduling/working_slot_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def working_slot_edit(request, pk):
    working_slot = get_object_or_404(WorkingSlot, pk=pk)
    if request.method == 'POST':
        form = WorkingSlotForm(request.POST, instance=working_slot)
        if form.is_valid():
            working_slot = form.save(commit=False)
            working_slot.end_time = (datetime.combine(datetime.min, working_slot.start_time) + working_slot.duration).time()
            working_slot.save()
            messages.success(request, 'Working slot updated successfully.')
            return redirect('working_slot_list')
    else:
        form = WorkingSlotForm(instance=working_slot)
    return render(request, 'scheduling/working_slot_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def working_slot_delete(request, pk):
    working_slot = get_object_or_404(WorkingSlot, pk=pk)
    if request.method == 'POST':
        working_slot.delete()
        messages.success(request, 'Working slot deleted successfully.')
        return redirect('working_slot_list')
    return render(request, 'scheduling/working_slot_confirm_delete.html', {'working_slot': working_slot})

# TechnicianAvailability views
@login_required
@user_passes_test(is_admin_or_manager)
def technician_availability_list(request):
    availabilities = TechnicianAvailability.objects.all()
    return render(request, 'scheduling/technician_availability_list.html', {'availabilities': availabilities})

@login_required
@user_passes_test(is_admin_or_manager)
def technician_availability_create(request):
    if request.method == 'POST':
        form = TechnicianAvailabilityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Technician availability created successfully.')
            return redirect('technician_availability_list')
    else:
        form = TechnicianAvailabilityForm()
    return render(request, 'scheduling/technician_availability_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def technician_availability_edit(request, pk):
    availability = get_object_or_404(TechnicianAvailability, pk=pk)
    if request.method == 'POST':
        form = TechnicianAvailabilityForm(request.POST, instance=availability)
        if form.is_valid():
            form.save()
            messages.success(request, 'Technician availability updated successfully.')
            return redirect('technician_availability_list')
    else:
        form = TechnicianAvailabilityForm(instance=availability)
    return render(request, 'scheduling/technician_availability_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def technician_availability_delete(request, pk):
    availability = get_object_or_404(TechnicianAvailability, pk=pk)
    if request.method == 'POST':
        availability.delete()
        messages.success(request, 'Technician availability deleted successfully.')
        return redirect('technician_availability_list')
    return render(request, 'scheduling/technician_availability_confirm_delete.html', {'availability': availability})