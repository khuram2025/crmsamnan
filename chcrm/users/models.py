from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password, **extra_fields):
        if not mobile:
            raise ValueError(_('The Mobile number must be set'))
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(mobile, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('TECHNICIAN', 'Technician'),
        ('CALL_CENTER_AGENT', 'Call Center Agent'),
        ('CUSTOMER', 'Customer'),
    )

    mobile = models.CharField(_('mobile number'), max_length=15, unique=True)
    email = models.EmailField(_('email address'), blank=True)
    role = models.CharField(max_length=20, choices=ROLES)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['role']

    objects = CustomUserManager()

    def __str__(self):
        return self.mobile