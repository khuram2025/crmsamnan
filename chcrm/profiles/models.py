from django.db import models
from django.conf import settings

class BaseProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        abstract = True

class CustomerProfile(BaseProfile):
    preferred_contact_method = models.CharField(max_length=20, choices=[('EMAIL', 'Email'), ('PHONE', 'Phone')], default='EMAIL')

class TechnicianProfile(BaseProfile):
    specialization = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)

class ManagerProfile(BaseProfile):
    department = models.CharField(max_length=100, blank=True)

class CallCenterAgentProfile(BaseProfile):
    shift = models.CharField(max_length=20, choices=[('DAY', 'Day'), ('NIGHT', 'Night')], default='DAY')