# crm/urls.py

from django.urls import path, include
from . import views
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

]