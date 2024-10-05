from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Service

admin.site.register(Service, DraggableMPTTAdmin)
