# crm/forms.py

from django import forms
from .models import Customer, Schedule, Slot, Technician, TechnicianSchedule
from accounts.models import CustomUser, Area, Service

class CustomerForm(forms.ModelForm):
    create_account = forms.BooleanField(required=False, label="Create Customer Account")

    class Meta:
        model = Customer
        fields = ['name', 'mobile_number',  'area', 'notes', 'create_account']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class TechnicianForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=17)  # Changed from mobile_number
    email = forms.EmailField()
    working_areas = forms.ModelMultipleChoiceField(
        queryset=Area.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Technician
        fields = ['technician_id', 'working_shift', 'working_areas']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['name'].initial = self.instance.name
            self.fields['mobile'].initial = self.instance.mobile_number
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        technician = super().save(commit=False)
        
        # Create or update the associated CustomUser
        if not technician.user_id:
            user = CustomUser.objects.create(
                mobile=self.cleaned_data['mobile'],
                email=self.cleaned_data['email'],
                is_technician=True
            )
            technician.user = user
        else:
            technician.user.mobile = self.cleaned_data['mobile']
            technician.user.email = self.cleaned_data['email']
            technician.user.save()

        if commit:
            technician.save()
            self.save_m2m()  # Save many-to-many data for working_areas

        return technician

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['name', 'slot_duration', 'custom_duration', 'start_time', 'end_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        slot_duration = cleaned_data.get('slot_duration')
        custom_duration = cleaned_data.get('custom_duration')
        if slot_duration == 0 and not custom_duration:
            raise forms.ValidationError("Custom duration must be set when slot duration is custom")
        return cleaned_data

class TechnicianScheduleForm(forms.ModelForm):
    class Meta:
        model = TechnicianSchedule
        fields = ['technician', 'schedule', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from .models import Appointment, Technician, Slot
from accounts.models import City, Area
from django.db.models import Q 

class AppointmentForm(forms.ModelForm):
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select a city")
    area = forms.ModelChoiceField(queryset=Area.objects.none(), empty_label="Select an area")
    technician = forms.ModelChoiceField(queryset=Technician.objects.none(), empty_label="Select a technician")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    slot = forms.ModelChoiceField(queryset=Slot.objects.none(), empty_label="Select a time slot", required=False)
    name = forms.CharField(max_length=100)
    mobile_number = forms.CharField(max_length=17)
    service = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), required=False)

    class Meta:
        model = Appointment
        fields = ['city', 'area', 'technician', 'name', 'mobile_number', 'notes', 'date', 'slot', 'service']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the current slot ID if editing an existing appointment
        current_slot_id = None
        if self.instance.pk:
            current_slot_id = self.instance.slot.pk
        
        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                self.fields['area'].queryset = Area.objects.filter(city_id=city_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('city'):
            try:
                city_id = int(self.initial.get('city'))
                self.fields['area'].queryset = Area.objects.filter(city_id=city_id)
            except (ValueError, TypeError):
                pass
        
        if 'area' in self.data:
            try:
                area_id = int(self.data.get('area'))
                self.fields['technician'].queryset = Technician.objects.filter(working_areas__id=area_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('area'):
            try:
                area_id = int(self.initial.get('area'))
                self.fields['technician'].queryset = Technician.objects.filter(working_areas__id=area_id)
            except (ValueError, TypeError):
                pass

        if 'technician' in self.data and 'date' in self.data:
            try:
                technician_id = int(self.data.get('technician'))
                date = self.data.get('date')
                slots = Slot.objects.filter(technician_id=technician_id, date=date)
                if current_slot_id:
                    slots = slots.filter(Q(appointment__isnull=True) | Q(pk=current_slot_id))
                else:
                    slots = slots.filter(appointment__isnull=True)
                self.fields['slot'].queryset = slots
            except (ValueError, TypeError):
                pass
        elif self.initial.get('technician') and self.initial.get('date'):
            try:
                technician_id = int(self.initial.get('technician'))
                date = self.initial.get('date')
                slots = Slot.objects.filter(technician_id=technician_id, date=date)
                if current_slot_id:
                    slots = slots.filter(Q(appointment__isnull=True) | Q(pk=current_slot_id))
                else:
                    slots = slots.filter(appointment__isnull=True)
                self.fields['slot'].queryset = slots
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        technician = cleaned_data.get('technician')
        date = cleaned_data.get('date')
        slot = cleaned_data.get('slot')

        print(f"Debug - Clean method: technician={technician}, date={date}, slot={slot}")
        print(f"Debug - Current instance: {self.instance.pk}")

        if not all([technician, date, slot]):
            raise forms.ValidationError("Please select a technician, date, and time slot.")

        if slot and slot.technician != technician:
            raise forms.ValidationError("The selected slot does not belong to the chosen technician.")

        if slot and slot.date != date:
            raise forms.ValidationError("The selected slot is not for the chosen date.")

        # Check if the slot is booked
        if slot:
            print(f"Debug - Slot: {slot}")
            print(f"Debug - Slot is_booked: {slot.is_booked()}")
            slot_appointment = getattr(slot, 'appointment', None)
            print(f"Debug - Slot appointment: {slot_appointment}")
            
            # If we're editing an existing appointment
            if self.instance.pk:
                print(f"Debug - Editing existing appointment: {self.instance.pk}")
                # If the slot is booked by another appointment
                if slot.is_booked() and slot_appointment and slot_appointment.pk != self.instance.pk:
                    raise forms.ValidationError("This slot is already booked by another appointment.")
            else:
                if slot.is_booked():
                    raise forms.ValidationError("This slot is already booked.")

        return cleaned_data





class AddTeamMemberForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['mobile', 'email', 'user_type', 'is_technician']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['is_technician'].initial = True
        self.fields['is_technician'].widget = forms.HiddenInput()
        self.fields['user_type'].choices = [
            ('MANAGER', 'Manager'),
            ('TECHNICIAN', 'Technician'),
        ]