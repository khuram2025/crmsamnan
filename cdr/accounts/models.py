from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    listening_port = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class UserType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, company=None, user_type=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        if company is None:
            company = Company.objects.get_or_create(name="Channab")[0]
        else:
            company, created = Company.objects.get_or_create(name=company)
        
        if user_type is None:
            user_type = UserType.objects.get_or_create(name="Customer")[0]
        else:
            user_type, created = UserType.objects.get_or_create(name=user_type)
        
        user = self.model(email=email, company=company, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, company=None, user_type='Admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, company, user_type, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')
    
    objects = CustomUserManager()
    
    REQUIRED_FIELDS = ['user_type']
    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return f"{self.email} - {self.user_type}"

    def is_admin(self):
        return self.user_type.name == 'Admin'

    def create_user(self, email, user_type, password=None):
        if not self.is_admin():
            raise ValidationError("Only admin users can create new users.")
        return CustomUser.objects.create_user(email=email, company=self.company, user_type=user_type, password=password)

    def update_user(self, user, **kwargs):
        if not self.is_admin() or user.company != self.company:
            raise ValidationError("You don't have permission to update this user.")
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()

    def delete_user(self, user):
        if not self.is_admin() or user.company != self.company:
            raise ValidationError("You don't have permission to delete this user.")
        user.delete()

    def list_company_users(self):
        if not self.is_admin():
            raise ValidationError("Only admin users can list company users.")
        return CustomUser.objects.filter(company=self.company)

class Extension(models.Model):
    extension = models.CharField(max_length=20)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='extensions')
    
    class Meta:
        unique_together = ('extension', 'company')
        ordering = ['company', 'extension']
    
    def __str__(self):
        return f"{self.extension} - {self.full_name or 'Unnamed'} ({self.company.name if self.company else 'No Company'})"
    
    def save(self, *args, **kwargs):
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)
        
        # Ensure a UserQuota is created for this extension
        from billing.models import UserQuota
        if not UserQuota.objects.filter(extension=self).exists():
            UserQuota.objects.create(extension=self)

# Create default user types
@receiver(post_save, sender=CustomUser)
def create_default_user_types(sender, **kwargs):
    UserType.objects.get_or_create(name="Call Center Agent")
    UserType.objects.get_or_create(name="Manager")
    UserType.objects.get_or_create(name="Customer")
    UserType.objects.get_or_create(name="Technician")
    UserType.objects.get_or_create(name="Admin")