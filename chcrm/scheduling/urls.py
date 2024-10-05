from django.urls import path
from . import views

urlpatterns = [
    # Shift URLs
    path('shifts/', views.shift_list, name='shift_list'),
    path('shifts/create/', views.shift_create, name='shift_create'),
    path('shifts/<int:pk>/edit/', views.shift_edit, name='shift_edit'),
    path('shifts/<int:pk>/delete/', views.shift_delete, name='shift_delete'),

    # WorkingSlot URLs
    path('working-slots/', views.working_slot_list, name='working_slot_list'),
    path('working-slots/create/', views.working_slot_create, name='working_slot_create'),
    path('working-slots/<int:pk>/edit/', views.working_slot_edit, name='working_slot_edit'),
    path('working-slots/<int:pk>/delete/', views.working_slot_delete, name='working_slot_delete'),

    # TechnicianAvailability URLs
    path('technician-availability/', views.technician_availability_list, name='technician_availability_list'),
    path('technician-availability/create/', views.technician_availability_create, name='technician_availability_create'),
    path('technician-availability/<int:pk>/edit/', views.technician_availability_edit, name='technician_availability_edit'),
    path('technician-availability/<int:pk>/delete/', views.technician_availability_delete, name='technician_availability_delete'),
]
