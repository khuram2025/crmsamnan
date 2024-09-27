from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from accounts.models import City, Area

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def add_city(request):
    name = request.POST.get('name')
    if name:
        city, created = City.objects.get_or_create(name=name)
        if created:
            return JsonResponse({'status': 'success', 'message': 'City added successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'City already exists.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid city name.'})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def add_area(request):
    name = request.POST.get('name')
    city_id = request.POST.get('city')
    parent_id = request.POST.get('parent')
    if name and city_id:
        try:
            city = City.objects.get(id=city_id)
            parent = Area.objects.get(id=parent_id) if parent_id else None
            area, created = Area.objects.get_or_create(name=name, city=city, parent=parent)
            if created:
                return JsonResponse({'status': 'success', 'message': 'Area added successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Area already exists in this city.'})
        except City.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid city.'})
        except Area.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid parent area.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid area name or city.'})

@user_passes_test(lambda u: u.is_superuser)
def get_cities_and_areas(request):
    cities = City.objects.all()
    data = []
    for city in cities:
        city_data = {
            'id': city.id,
            'name': city.name,
            'areas': get_areas_with_subareas(city)
        }
        data.append(city_data)
    return JsonResponse(data, safe=False)

def get_areas_with_subareas(city, parent=None):
    areas = []
    for area in Area.objects.filter(city=city, parent=parent):
        area_data = {
            'id': area.id,
            'name': area.name,
            'parent': {'id': area.parent.id, 'name': area.parent.name} if area.parent else None,
            'sub_areas': get_areas_with_subareas(city, parent=area)
        }
        areas.append(area_data)
    return areas

def get_area_hierarchy(areas):
    result = []
    for area in areas:
        area_data = {
            'id': area.id,
            'name': area.name,
            'sub_areas': get_area_hierarchy(area.sub_areas.all())
        }
        result.append(area_data)
    return result

from django.http import JsonResponse
from accounts.models import City, Area

@user_passes_test(lambda u: u.is_superuser)
def get_cities(request):
    cities = City.objects.all().values('id', 'name')
    return JsonResponse(list(cities), safe=False)

@user_passes_test(lambda u: u.is_superuser)
def get_areas_by_city(request):
    city_id = request.GET.get('city_id')
    if city_id:
        areas = Area.objects.filter(city_id=city_id, parent=None).values('id', 'name')
        return JsonResponse(list(areas), safe=False)
    return JsonResponse([], safe=False)

@user_passes_test(lambda u: u.is_superuser)
def get_city(request):
    city_id = request.GET.get('id')
    try:
        city = City.objects.get(id=city_id)
        return JsonResponse({'id': city.id, 'name': city.name})
    except City.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'City not found.'})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def edit_city(request):
    city_id = request.POST.get('id')
    name = request.POST.get('name')
    try:
        city = City.objects.get(id=city_id)
        city.name = name
        city.save()
        return JsonResponse({'status': 'success', 'message': 'City updated successfully.'})
    except City.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'City not found.'})

import json
from django.views.decorators.csrf import csrf_exempt

@user_passes_test(lambda u: u.is_superuser)
@csrf_exempt  # Only for debugging, remove in production
@require_POST
def delete_city(request):
    try:
        data = json.loads(request.body)
        city_id = data.get('id')
        city = City.objects.get(id=city_id)
        city.delete()
        return JsonResponse({'status': 'success', 'message': 'City deleted successfully.'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'})
    except City.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'City not found.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@user_passes_test(lambda u: u.is_superuser)
def get_area(request):
    area_id = request.GET.get('id')
    try:
        area = Area.objects.get(id=area_id)
        return JsonResponse({
            'id': area.id,
            'name': area.name,
            'city': {'id': area.city.id, 'name': area.city.name},
            'parent': {'id': area.parent.id, 'name': area.parent.name} if area.parent else None
        })
    except Area.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Area not found.'})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def edit_area(request):
    area_id = request.POST.get('id')
    name = request.POST.get('name')
    city_id = request.POST.get('city')
    parent_id = request.POST.get('parent')
    try:
        area = Area.objects.get(id=area_id)
        area.name = name
        area.city = City.objects.get(id=city_id)
        area.parent = Area.objects.get(id=parent_id) if parent_id else None
        area.save()
        return JsonResponse({'status': 'success', 'message': 'Area updated successfully.'})
    except (Area.DoesNotExist, City.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Area or City not found.'})

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def delete_area(request):
    try:
        data = json.loads(request.body)
        area_id = data.get('id')
        area = Area.objects.get(id=area_id)
        area.delete()
        return JsonResponse({'status': 'success', 'message': 'Area deleted successfully.'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'})
    except Area.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Area not found.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
