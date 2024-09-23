# accounts/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),  # Changed to custom login view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('test/', views.test_page, name='test_page'),
    path('appointment-booking/', views.appointment_booking, name='appointment_booking'),
    path('get-areas/', views.get_areas, name='get_areas'),
]