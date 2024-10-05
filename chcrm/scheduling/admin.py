from django.contrib import admin
from .models import Shift, WorkingSlot, TechnicianAvailability

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(WorkingSlot)
class WorkingSlotAdmin(admin.ModelAdmin):
    list_display = ('shift', 'start_time', 'end_time', 'gap_between_slots')
    list_filter = ('shift',)
    search_fields = ('shift__name',)

@admin.register(TechnicianAvailability)
class TechnicianAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('technician', 'date', 'shift', 'slot', 'is_available')
    list_filter = ('technician', 'date', 'shift', 'is_available')
    search_fields = ('technician__user__email', 'date')
    date_hierarchy = 'date'
