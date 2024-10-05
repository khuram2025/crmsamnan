from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomerProfile, TechnicianProfile, ManagerProfile, CallCenterAgentProfile

admin.site.register(CustomerProfile)
admin.site.register(TechnicianProfile)
admin.site.register(ManagerProfile)
admin.site.register(CallCenterAgentProfile)