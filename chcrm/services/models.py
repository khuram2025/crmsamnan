from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Service(MPTTModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

# Add this to the existing models.py file
from django.conf import settings

class ServiceAssignment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('service', 'technician')

    def __str__(self):
        return f"{self.service} assigned to {self.technician}"