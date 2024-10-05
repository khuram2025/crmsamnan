from django.urls import path
from .views import SignUpView, custom_logout


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', custom_logout, name='logout'),
]