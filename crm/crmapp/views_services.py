from django.http import JsonResponse
from django.views.decorators.http import require_POST
from accounts.models import Service
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

def get_services(request):
    print("get_services view called")
    services = Service.objects.all()
    data = [{
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'price': str(service.price),
        'parent': {'id': service.parent.id, 'name': service.parent.name} if service.parent else None
    } for service in services]
    return JsonResponse(data, safe=False)

@require_POST
def add_service(request):
    print("add_service view called")
    name = request.POST.get('name')
    description = request.POST.get('description')
    price = request.POST.get('price')
    parent_id = request.POST.get('parent')
    
    print(f"Attempting to add service: {name}, {description}, {price}, parent_id: {parent_id}")
    
    try:
        parent = Service.objects.get(id=parent_id) if parent_id else None
        service = Service.objects.create(name=name, description=description, price=price, parent=parent)
        print(f"Service added successfully: {service}")
        return JsonResponse({'status': 'success', 'message': 'Service added successfully'})
    except Exception as e:
        logger.error(f"Error adding service: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def edit_service(request):
    print("edit_service view called")
    service_id = request.POST.get('id')
    name = request.POST.get('name')
    description = request.POST.get('description')
    price = request.POST.get('price')
    parent_id = request.POST.get('parent')
    
    try:
        service = Service.objects.get(id=service_id)
        service.name = name
        service.description = description
        service.price = price
        service.parent = Service.objects.get(id=parent_id) if parent_id else None
        service.save()
        return JsonResponse({'status': 'success', 'message': 'Service updated successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def delete_service(request):
    print("delete_service view called")
    service_id = request.POST.get('id')
    try:
        service = Service.objects.get(id=service_id)
        service.delete()
        return JsonResponse({'status': 'success', 'message': 'Service deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_service(request):
    print("get_service view called")
    service_id = request.GET.get('id')
    service = get_object_or_404(Service, id=service_id)
    data = {
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'price': str(service.price),
        'parent': {'id': service.parent.id, 'name': service.parent.name} if service.parent else None
    }
    return JsonResponse(data)