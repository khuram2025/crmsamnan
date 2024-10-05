from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Technician, Area
import json
from django.core.exceptions import ValidationError

@user_passes_test(lambda u: u.is_superuser)
def get_technicians(request):
    technicians = Technician.objects.all()
    data = [{
        'user_id': tech.user_id,
        'technician_id': tech.technician_id,
        'name': tech.name,
        'mobile': tech.mobile_number,
        'email': tech.user.email,
        'working_shift': tech.working_shift,
    } for tech in technicians]
    return JsonResponse(data, safe=False)

@user_passes_test(lambda u: u.is_superuser)
def get_technician(request):
    technician_id = request.GET.get('id')
    try:
        technician = Technician.objects.get(technician_id=technician_id)
        data = {
            'user_id': technician.user_id,
            'technician_id': technician.technician_id,
            'name': technician.name,
            'mobile': technician.mobile_number,
            'email': technician.user.email,
            'working_shift': technician.working_shift,
            'working_areas': [{'id': area.id, 'name': area.name} for area in technician.working_areas.all()]
        }
        return JsonResponse(data)
    except Technician.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Technician not found.'})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def add_technician(request):
    form_data = request.POST.copy()
    working_areas = request.POST.getlist('working_areas')
    form_data.setlist('working_areas', working_areas)
    form = TechnicianForm(form_data)
    if form.is_valid():
        technician = form.save()
        return JsonResponse({'status': 'success', 'message': 'Technician added successfully.'})
    else:
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({'status': 'error', 'errors': errors}, status=400)

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def edit_technician(request):
    print("Received edit request")
    print("POST data:", request.POST)
    
    old_technician_id = request.POST.get('old_technician_id')
    new_technician_id = request.POST.get('technician_id')
    print("Old Technician ID:", old_technician_id)
    print("New Technician ID:", new_technician_id)
    
    try:
        technician = Technician.objects.get(technician_id=old_technician_id)
        print("Found technician:", technician)
        
        # Update user fields
        name_parts = request.POST.get('name').split(maxsplit=1)
        technician.user.first_name = name_parts[0]
        technician.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        technician.user.email = request.POST.get('email')
        technician.user.mobile = request.POST.get('mobile')
        
        # Update technician fields
        technician.technician_id = new_technician_id
        technician.working_shift = request.POST.get('working_shift')
        
        # Update working areas
        working_area_ids = request.POST.getlist('working_areas')
        technician.working_areas.set(Area.objects.filter(id__in=working_area_ids))
        
        print("Updated fields:")
        print(f"Name: {technician.user.get_full_name()}")
        print(f"Email: {technician.user.email}")
        print(f"Mobile: {technician.user.mobile}")
        print(f"Working Shift: {technician.working_shift}")
        print(f"New Technician ID: {technician.technician_id}")
        print(f"Working Areas: {', '.join(str(area.id) for area in technician.working_areas.all())}")
        
        technician.user.save()
        technician.save()
        
        print("Technician updated successfully")
        return JsonResponse({'status': 'success', 'message': 'Technician updated successfully.'})
    except Technician.DoesNotExist:
        print(f"Technician not found with ID: {old_technician_id}")
        return JsonResponse({'status': 'error', 'message': 'Technician not found.'})
    except Exception as e:
        print("Unexpected error:", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def delete_technician(request):
    try:
        data = json.loads(request.body)
        technician_id = data.get('id')
        technician = Technician.objects.get(technician_id=technician_id)
        technician.user.delete()  # This will also delete the technician due to the CASCADE relationship
        return JsonResponse({'status': 'success', 'message': 'Technician deleted successfully.'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'})
    except Technician.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Technician not found.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})