from django.urls import path
from . import views

urlpatterns = [
    # City URLs
    path('cities/', views.CityListView.as_view(), name='city_list'),
    path('cities/create/', views.CityCreateView.as_view(), name='city_create'),
    path('cities/<int:pk>/update/', views.CityUpdateView.as_view(), name='city_update'),
    path('cities/<int:pk>/delete/', views.CityDeleteView.as_view(), name='city_delete'),

    # Area URLs
    path('areas/', views.AreaListView.as_view(), name='area_list'),
    path('areas/create/', views.AreaCreateView.as_view(), name='area_create'),
    path('areas/<int:pk>/update/', views.AreaUpdateView.as_view(), name='area_update'),
    path('areas/<int:pk>/delete/', views.AreaDeleteView.as_view(), name='area_delete'),

    # Technician Area Assignment URLs
    path('technician-area-assignments/', views.TechnicianAreaAssignmentListView.as_view(), name='technician_area_assignment_list'),
    path('technician-area-assignments/create/', views.TechnicianAreaAssignmentCreateView.as_view(), name='technician_area_assignment_create'),
    path('technician-area-assignments/<int:pk>/update/', views.TechnicianAreaAssignmentUpdateView.as_view(), name='technician_area_assignment_update'),
    path('technician-area-assignments/<int:pk>/delete/', views.TechnicianAreaAssignmentDeleteView.as_view(), name='technician_area_assignment_delete'),
]