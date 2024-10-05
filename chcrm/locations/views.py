from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import City, Area, TechnicianAreaAssignment
from .forms import CityForm, AreaForm, TechnicianAreaAssignmentForm
from django.contrib import messages

def is_manager_or_admin(user):
    return user.role in ['MANAGER', 'ADMIN']

class ManagerAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_manager_or_admin(self.request.user)

# City views
class CityListView(LoginRequiredMixin, ManagerAdminRequiredMixin, ListView):
    model = City
    template_name = 'locations/city_list.html'
    context_object_name = 'cities'

class CityCreateView(LoginRequiredMixin, ManagerAdminRequiredMixin, CreateView):
    model = City
    form_class = CityForm
    template_name = 'locations/city_form.html'
    success_url = reverse_lazy('city_list')

class CityUpdateView(LoginRequiredMixin, ManagerAdminRequiredMixin, UpdateView):
    model = City
    form_class = CityForm
    template_name = 'locations/city_form.html'
    success_url = reverse_lazy('city_list')

class CityDeleteView(LoginRequiredMixin, ManagerAdminRequiredMixin, DeleteView):
    model = City
    template_name = 'locations/city_confirm_delete.html'
    success_url = reverse_lazy('city_list')

# Area views
class AreaListView(LoginRequiredMixin, ManagerAdminRequiredMixin, ListView):
    model = Area
    template_name = 'locations/area_list.html'
    context_object_name = 'areas'

class AreaCreateView(LoginRequiredMixin, ManagerAdminRequiredMixin, CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'locations/area_form.html'
    success_url = reverse_lazy('area_list')

class AreaUpdateView(LoginRequiredMixin, ManagerAdminRequiredMixin, UpdateView):
    model = Area
    form_class = AreaForm
    template_name = 'locations/area_form.html'
    success_url = reverse_lazy('area_list')

class AreaDeleteView(LoginRequiredMixin, ManagerAdminRequiredMixin, DeleteView):
    model = Area
    template_name = 'locations/area_confirm_delete.html'
    success_url = reverse_lazy('area_list')

# Technician Area Assignment views
def is_admin_or_manager(user):
    return user.role in ['ADMIN', 'MANAGER']

class AdminManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin_or_manager(self.request.user)

class TechnicianAreaAssignmentListView(LoginRequiredMixin, AdminManagerRequiredMixin, ListView):
    model = TechnicianAreaAssignment
    template_name = 'locations/technician_area_assignment_list.html'
    context_object_name = 'assignments'

class TechnicianAreaAssignmentCreateView(LoginRequiredMixin, AdminManagerRequiredMixin, CreateView):
    model = TechnicianAreaAssignment
    form_class = TechnicianAreaAssignmentForm
    template_name = 'locations/technician_area_assignment_form.html'
    success_url = reverse_lazy('technician_area_assignment_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Area assigned to technician successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error assigning area to technician. Please check the form.')
        return super().form_invalid(form)

class TechnicianAreaAssignmentUpdateView(LoginRequiredMixin, AdminManagerRequiredMixin, UpdateView):
    model = TechnicianAreaAssignment
    form_class = TechnicianAreaAssignmentForm
    template_name = 'locations/technician_area_assignment_form.html'
    success_url = reverse_lazy('technician_area_assignment_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Assignment updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating assignment. Please check the form.')
        return super().form_invalid(form)

class TechnicianAreaAssignmentDeleteView(LoginRequiredMixin, AdminManagerRequiredMixin, DeleteView):
    model = TechnicianAreaAssignment
    template_name = 'locations/technician_area_assignment_confirm_delete.html'
    success_url = reverse_lazy('technician_area_assignment_list')