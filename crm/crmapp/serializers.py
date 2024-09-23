# crm/serializers.py

from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    create_account = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Customer
        fields = ['name', 'mobile_number', 'city', 'area', 'notes', 'create_account']
    
# crm/serializers.py

from rest_framework import serializers
from .models import Schedule, Slot, TechnicianSchedule

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['id', 'start_time', 'end_time']

class ScheduleSerializer(serializers.ModelSerializer):
    slots = SlotSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'name', 'slot_duration', 'custom_duration', 'start_time', 'end_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                  'slots']

class TechnicianScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianSchedule
        fields = ['id', 'technician', 'schedule', 'start_date', 'end_date']