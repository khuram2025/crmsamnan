# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Company, UserType, City, Area, Service, Appointment

class AreaInline(admin.TabularInline):
    model = Area
    extra = 1

class CityAdmin(admin.ModelAdmin):
    inlines = [AreaInline]
    list_display = ('name',)
    search_fields = ('name',)

class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    list_filter = ('city',)
    search_fields = ('name', 'city__name')

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.html import escape
from django.http import Http404

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    change_password_form = AdminPasswordChangeForm
    model = CustomUser
    list_display = ('mobile', 'email', 'company', 'user_type', 'is_staff', 'is_active', 'is_technician')
    list_filter = ('company', 'user_type', 'is_staff', 'is_active', 'is_technician')
    fieldsets = (
        (None, {'fields': ('mobile', 'email', 'password')}),
        ('Company Info', {'fields': ('company', 'user_type')}),
        ('Technician Info', {'fields': ('is_technician', 'service_areas')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'email', 'company', 'user_type', 'password1', 'password2', 'is_staff', 'is_active', 'is_technician', 'service_areas')}
        ),
    )
    search_fields = ('mobile', 'email')
    ordering = ('mobile',)
    filter_horizontal = ('service_areas',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('mobile',)
        return self.readonly_fields

    actions = ['reset_password']

    def reset_password(self, request, queryset):
        for user in queryset:
            password = CustomUser.objects.make_random_password()
            user.set_password(password)
            user.save()
            self.message_user(request, f"Password for {user.mobile} has been reset to: {password}")
    reset_password.short_description = "Reset password for selected users"

    def get_urls(self):
        from django.urls import path
        return [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super().get_urls()

    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, id)
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = _('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'technician', 'service', 'area', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date', 'service', 'area')
    search_fields = ('customer__mobile', 'technician__mobile', 'service__name')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company)
admin.site.register(UserType)
admin.site.register(City, CityAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Appointment, AppointmentAdmin)