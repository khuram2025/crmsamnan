from django.db import models
from django.conf import settings

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Area(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    parent_area = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='sub_areas')

    def __str__(self):
        return f'{self.name} ({self.city.name})'

class TechnicianAreaAssignment(models.Model):
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'TECHNICIAN'})
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('technician', 'area')

    def __str__(self):
        return f'{self.technician.mobile} - {self.area}'
