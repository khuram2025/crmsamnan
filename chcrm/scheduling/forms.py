from django import forms
from .models import Shift, WorkingSlot, TechnicianAvailability
from datetime import timedelta

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'start_time', 'end_time']

class WorkingSlotForm(forms.ModelForm):
    duration = forms.DurationField(help_text="Duration of each slot. Format: HH:MM:SS")
    gap_between_slots = forms.DurationField(required=False, help_text="Optional gap between slots. Format: HH:MM:SS")

    class Meta:
        model = WorkingSlot
        fields = ['shift', 'duration', 'gap_between_slots']
        widgets = {
            'shift': forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        shift = cleaned_data.get('shift')
        duration = cleaned_data.get('duration')

        if shift and duration:
            total_duration = timedelta(hours=shift.end_time.hour, minutes=shift.end_time.minute) - timedelta(hours=shift.start_time.hour, minutes=shift.start_time.minute)
            if duration > total_duration:
                raise forms.ValidationError("Duration exceeds the total time of the shift.")
        return cleaned_data

class TechnicianAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TechnicianAvailability
        fields = ['technician', 'date', 'shift', 'slot', 'is_available']