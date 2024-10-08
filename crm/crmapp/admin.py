# crm/admin.py

from django.contrib import admin
from .models import CustomUser, Customer, Technician
from accounts.models import City, Area, Service

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile_number',  'area', 'created_by', 'created_at', 'creation_method', 'create_account')
    list_filter = ('created_at', 'creation_method', 'create_account')
    search_fields = ('name', 'mobile_number',  'area')
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'creation_method')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            obj.creation_method = 'AGENT'
        super().save_model(request, obj, form, change)

        if obj.create_account and not obj.user:
            # Create a CustomUser for this customer
            password = CustomUser.objects.make_random_password()
            user = CustomUser.objects.create_user(
                mobile=obj.mobile_number,
                password=password
            )
            obj.user = user
            obj.save()
            self.message_user(request, f"Customer account created with temporary password: {password}")
            


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'technician_id', 'get_mobile_number', 'get_working_areas', 'working_shift', 'get_services', 'created_by', 'created_at')
    list_filter = ('working_shift', 'created_at', 'working_areas', 'services')
    search_fields = ('user__first_name', 'user__last_name', 'technician_id', 'user__mobile', 'working_areas__name', 'services__name')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    filter_horizontal = ('working_areas', 'services')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

    def get_mobile_number(self, obj):
        return obj.user.mobile
    get_mobile_number.short_description = 'Mobile Number'

    def get_working_areas(self, obj):
        return ", ".join([area.name for area in obj.working_areas.all()])
    get_working_areas.short_description = 'Working Areas'

    def get_services(self, obj):
        return ", ".join([service.name for service in obj.services.all()])
    get_services.short_description = 'Services'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        if not obj.user:
            # Create a CustomUser for this technician
            password = CustomUser.objects.make_random_password()
            user = CustomUser.objects.create_user(
                mobile=form.cleaned_data.get('mobile_number'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                password=password,
                is_technician=True
            )
            obj.user = user
            obj.save()
            
            # Assign services
            if 'services' in form.cleaned_data:
                obj.services.set(form.cleaned_data['services'])
            
            self.message_user(request, f"Technician account created with temporary password: {password}")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # This is an add form
            form.base_fields['first_name'] = forms.CharField(max_length=30)
            form.base_fields['last_name'] = forms.CharField(max_length=150)
            form.base_fields['mobile_number'] = forms.CharField(max_length=17)
            form.base_fields['services'] = forms.ModelMultipleChoiceField(
                queryset=Service.objects.all(),
                required=False,
                widget=admin.widgets.FilteredSelectMultiple('Services', False)
            )
        return form

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if 'services' in form.cleaned_data:
            form.instance.services.set(form.cleaned_data['services'])

# crm/admin.py

from django.contrib import admin
from .models import Schedule, Slot, TechnicianSchedule

class SlotInline(admin.TabularInline):
    model = Slot
    extra = 0

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slot_duration', 'start_time', 'end_time', 'get_working_days')
    list_filter = ('slot_duration', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
    search_fields = ('name',)
    inlines = [SlotInline]

    def get_working_days(self, obj):
        days = []
        if obj.monday: days.append('Mon')
        if obj.tuesday: days.append('Tue')
        if obj.wednesday: days.append('Wed')
        if obj.thursday: days.append('Thu')
        if obj.friday: days.append('Fri')
        if obj.saturday: days.append('Sat')
        if obj.sunday: days.append('Sun')
        return ', '.join(days)
    get_working_days.short_description = 'Working Days'



from .models import Appointment, TechnicianSchedule, Slot

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'get_technician', 'get_date', 'get_time', 'status')
    list_filter = ('status', 'slot__date', 'slot__technician')
    search_fields = ('customer__name', 'slot__technician__name')
    date_hierarchy = 'slot__date'

    def get_technician(self, obj):
        return obj.slot.technician
    get_technician.short_description = 'Technician'

    def get_date(self, obj):
        return obj.slot.date
    get_date.short_description = 'Date'

    def get_time(self, obj):
        return f"{obj.slot.start_time.strftime('%H:%M')} - {obj.slot.end_time.strftime('%H:%M')}"
    get_time.short_description = 'Time'

@admin.register(TechnicianSchedule)
class TechnicianScheduleAdmin(admin.ModelAdmin):
    list_display = ('technician', 'schedule', 'start_date', 'end_date')
    list_filter = ('technician', 'schedule', 'start_date')
    search_fields = ('technician__name', 'schedule__name')

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('technician', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('technician', 'date')
    search_fields = ('technician__name',)
    date_hierarchy = 'date'

    def is_booked(self, obj):
        return hasattr(obj, 'appointment')
    is_booked.boolean = True