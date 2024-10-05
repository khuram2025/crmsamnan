from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Service
from .forms import ServiceForm
from django.contrib import messages
from .models import ServiceAssignment
from users.models import User

def is_admin_or_manager(user):
    return user.is_authenticated and user.role in ['ADMIN', 'MANAGER']

@login_required
@user_passes_test(is_admin_or_manager)
def service_list(request):
    services = Service.objects.all()
    return render(request, 'services/service_list.html', {'services': services})

@login_required
@user_passes_test(is_admin_or_manager)
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'services/service_detail.html', {'service': service})

@login_required
@user_passes_test(is_admin_or_manager)
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form})

@login_required
@user_passes_test(is_admin_or_manager)
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_list')
    return render(request, 'services/service_confirm_delete.html', {'service': service})

@login_required
@user_passes_test(is_admin_or_manager)
def assign_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    technicians = User.objects.filter(role='TECHNICIAN')
    
    if request.method == 'POST':
        technician_id = request.POST.get('technician')
        technician = get_object_or_404(User, id=technician_id)
        
        assignment, created = ServiceAssignment.objects.get_or_create(
            service=service,
            technician=technician
        )
        
        if created:
            messages.success(request, f"Service '{service.name}' assigned to {technician.mobile}")
        else:
            messages.info(request, f"Service '{service.name}' is already assigned to {technician.mobile}")
        
        return redirect('service_detail', pk=service.pk)
    
    return render(request, 'services/assign_service.html', {'service': service, 'technicians': technicians})

