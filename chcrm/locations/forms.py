from django import forms
from .models import City, Area, TechnicianAreaAssignment
from users.models import User

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name']

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['city', 'name', 'parent_area']

class TechnicianAreaAssignmentForm(forms.ModelForm):
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(role='TECHNICIAN'),
        empty_label="Select a Technician"
    )

    class Meta:
        model = TechnicianAreaAssignment
        fields = ['technician', 'area']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = Area.objects.all()