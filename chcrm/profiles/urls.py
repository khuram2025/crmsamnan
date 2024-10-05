from django.urls import path
from .views import ProfileUpdateView
from . import views

urlpatterns = [
    path('update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/', views.user_profile, name='user_profile'),
]