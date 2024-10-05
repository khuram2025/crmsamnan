from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import CustomerProfile, TechnicianProfile, ManagerProfile, CallCenterAgentProfile
from .forms import CustomerProfileForm, TechnicianProfileForm, ManagerProfileForm, CallCenterAgentProfileForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'profiles/profile_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        user = self.request.user
        if user.role == 'CUSTOMER':
            return CustomerProfile.objects.get_or_create(user=user)[0]
        elif user.role == 'TECHNICIAN':
            return TechnicianProfile.objects.get_or_create(user=user)[0]
        elif user.role == 'MANAGER':
            return ManagerProfile.objects.get_or_create(user=user)[0]
        elif user.role == 'CALL_CENTER_AGENT':
            return CallCenterAgentProfile.objects.get_or_create(user=user)[0]

    def get_form_class(self):
        user = self.request.user
        if user.role == 'CUSTOMER':
            return CustomerProfileForm
        elif user.role == 'TECHNICIAN':
            return TechnicianProfileForm
        elif user.role == 'MANAGER':
            return ManagerProfileForm
        elif user.role == 'CALL_CENTER_AGENT':
            return CallCenterAgentProfileForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from scheduling.models import TechnicianAvailability
from services.models import ServiceAssignment

@login_required
def user_profile(request):
    user = request.user
    context = {
        'user': user,
        'schedules': TechnicianAvailability.objects.filter(technician__user=user) if user.role == 'TECHNICIAN' else None,
        'services': ServiceAssignment.objects.filter(technician=user) if user.role == 'TECHNICIAN' else None,
    }
    return render(request, 'profiles/user_profile.html', context)