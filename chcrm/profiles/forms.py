from django import forms
from .models import CustomerProfile, TechnicianProfile, ManagerProfile, CallCenterAgentProfile

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['full_name', 'address', 'preferred_contact_method']

class TechnicianProfileForm(forms.ModelForm):
    class Meta:
        model = TechnicianProfile
        fields = ['full_name', 'address', 'specialization', 'years_of_experience']

class ManagerProfileForm(forms.ModelForm):
    class Meta:
        model = ManagerProfile
        fields = ['full_name', 'address', 'department']

class CallCenterAgentProfileForm(forms.ModelForm):
    class Meta:
        model = CallCenterAgentProfile
        fields = ['full_name', 'address', 'shift']