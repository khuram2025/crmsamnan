# crm/urls.py

from django.urls import path, include
from . import views
from . import views_services, views_areas
from rest_framework.routers import DefaultRouter


urlpatterns = [
    # ... existing url patterns ...
    path('technicians/', views.technician_list, name='technician_list'),
    path('technicians/add/', views.technician_add, name='technician_add'),
    path('technicians/<int:pk>/edit/', views.technician_edit, name='technician_edit'),
    path('technicians/<int:pk>/delete/', views.technician_delete, name='technician_delete'),

    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.schedule_create, name='schedule_create'),
    path('schedules/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedules/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    path('technician-schedules/', views.technician_schedule_list, name='technician_schedule_list'),
    path('technician-schedules/create/', views.technician_schedule_create, name='technician_schedule_create'),
    path('technician-schedules/<int:pk>/edit/', views.technician_schedule_edit, name='technician_schedule_edit'),
    path('technician-schedules/<int:pk>/delete/', views.technician_schedule_delete, name='technician_schedule_delete'),


    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('ajax/load-areas/', views.load_areas, name='ajax_load_areas'),
    path('ajax/load-technicians/', views.load_technicians, name='ajax_load_technicians'),
    path('ajax/load-slots/', views.load_slots, name='ajax_load_slots'),
    path('ajax/get-or-create-customer/', views.get_or_create_customer, name='ajax_get_or_create_customer'),

    path('appointments/<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('get-available-slots/', views.get_available_slots, name='get_available_slots'),

    path('add-team-member/', views.add_team_member, name='add_team_member'),

    path('add-city/', views_areas.add_city, name='add_city'),
    path('add-area/', views_areas.add_area, name='add_area'),
    path('get-cities-and-areas/', views_areas.get_cities_and_areas, name='get_cities_and_areas'),
    path('get-areas-by-city/', views_areas.get_areas_by_city, name='get_areas_by_city'),

    path('get-cities/', views_areas.get_cities, name='get_cities'),
    path('get-city/', views_areas.get_city, name='get_city'),
    path('edit-city/', views_areas.edit_city, name='edit_city'),
    path('delete-city/', views_areas.delete_city, name='delete_city'),
    path('get-area/', views_areas.get_area, name='get_area'),
    path('edit-area/', views_areas.edit_area, name='edit_area'),
    path('delete-area/', views_areas.delete_area, name='delete_area'),


    # ... other url patterns ...
    path('get-services/', views_services.get_services, name='get_services'),
    path('add-service/', views_services.add_service, name='add_service'),
    path('edit-service/', views_services.edit_service, name='edit_service'),
    path('delete-service/', views_services.delete_service, name='delete_service'),
    path('get-service/', views_services.get_service, name='get_service'),

]