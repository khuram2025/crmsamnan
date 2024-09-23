# accounts/models.py

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator
from .managers import CustomUserManager

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Area(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='areas')

    class Meta:
        unique_together = ('name', 'city')

    def __str__(self):
        return f"{self.name}, {self.city.name}"

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    mobile = models.CharField(
        _('mobile number'),
        max_length=17,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, related_name='employees', null=True, blank=True)
    user_type = models.ForeignKey('UserType', on_delete=models.SET_NULL, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # New fields for technicians
    is_technician = models.BooleanField(default=False)
    service_areas = models.ManyToManyField('Area', related_name='service_users', blank=True)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.mobile

    def get_full_name(self):
        return self.mobile

    def get_short_name(self):
        return self.mobile

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments_as_customer')
    technician = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='appointments_as_technician')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')

    def __str__(self):
        return f"Appointment for {self.customer} on {self.appointment_date} at {self.appointment_time}"