# crm/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.models import Area, CustomUser, Service


CustomUser = get_user_model()

class Customer(models.Model):
    CREATION_METHODS = (
        ('AGENT', 'Added by Call Center Agent'),
        ('SELF', 'Self Signup'),
        ('API', 'Added via API'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=17, unique=True)
   
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, related_name='customers')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creation_method = models.CharField(max_length=5, choices=CREATION_METHODS, default='AGENT')
    create_account = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.mobile_number}"

class Technician(models.Model):
    SHIFT_CHOICES = (
        ('MORNING', 'Morning Shift'),
        ('AFTERNOON', 'Afternoon Shift'),
        ('NIGHT', 'Night Shift'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    technician_id = models.CharField(max_length=20, unique=True)
    working_areas = models.ManyToManyField(Area, related_name='crmapp_technicians')
    working_shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_technicians')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    services = models.ManyToManyField(Service, related_name='technicians', blank=True)
    

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.technician_id}"

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def mobile_number(self):
        return self.user.mobile

class Schedule(models.Model):
    DURATION_CHOICES = [
        (30, '30 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours'),
        (0, 'Custom'),
    ]

    name = models.CharField(max_length=100)
    slot_duration = models.IntegerField(choices=DURATION_CHOICES)
    custom_duration = models.IntegerField(null=True, blank=True, help_text="Duration in minutes if custom is selected")
    start_time = models.TimeField()
    end_time = models.TimeField()
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.slot_duration == 0 and not self.custom_duration:
            raise ValidationError("Custom duration must be set when slot duration is custom")
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

    def get_duration(self):
        return self.custom_duration if self.slot_duration == 0 else self.slot_duration


from django.db import models
from django.utils import timezone

def get_current_date():
    return timezone.now().date()

class Slot(models.Model):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='slots')
    technician = models.ForeignKey('Technician', on_delete=models.CASCADE, related_name='slots', null=True, blank=True)
    date = models.DateField(default=get_current_date)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('schedule', 'date', 'start_time', 'end_time')


    def is_booked(self):
        try:
            return self.appointment is not None
        except Slot.appointment.RelatedObjectDoesNotExist:
            return False

    def __str__(self):
        return f"{self.technician}: {self.date} {self.start_time} - {self.end_time}"
# crm/models.py

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, datetime, time

class TechnicianSchedule(models.Model):
    technician = models.ForeignKey('Technician', on_delete=models.CASCADE, related_name='schedules')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.technician.name} - {self.schedule.name} ({self.start_date} to {self.end_date or 'ongoing'})"

    class Meta:
        # Remove the unique_together constraint
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')) | models.Q(end_date__isnull=True),
                name='end_date_after_start_date'
            )
        ]
    def check_conflicts(self):
        overlapping_schedules = TechnicianSchedule.objects.filter(
            technician=self.technician,
            start_date__lte=self.end_date or datetime.max.date(),
            end_date__gte=self.start_date
        ).exclude(pk=self.pk)

        for overlap in overlapping_schedules:
            if (self.schedule.start_time < overlap.schedule.end_time and
                self.schedule.end_time > overlap.schedule.start_time):
                return True
        return False

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.generate_slots()

    def generate_slots(self):
        current_date = self.start_date
        end_date = self.end_date or (current_date + timedelta(days=365))  # Generate for a year if no end_date

        while current_date <= end_date:
            if self.is_working_day(current_date):
                self.create_day_slots(current_date)
            current_date += timedelta(days=1)

    def is_working_day(self, date):
        day_name = date.strftime("%A").lower()
        return getattr(self.schedule, day_name)

    def create_day_slots(self, date):
        start_time = datetime.combine(date, self.schedule.start_time)
        end_time = datetime.combine(date, self.schedule.end_time)
        slot_duration = timedelta(minutes=self.schedule.get_duration())

        while start_time + slot_duration <= end_time:
            Slot.objects.create(
                schedule=self.schedule,
                technician=self.technician,
                date=date,
                start_time=start_time.time(),
                end_time=(start_time + slot_duration).time()
            )
            start_time += slot_duration

@receiver(post_save, sender=TechnicianSchedule)
def update_slots(sender, instance, created, **kwargs):
    if not created:
        # Delete existing slots
        Slot.objects.filter(technician=instance.technician, date__gte=instance.start_date).delete()
        # Regenerate slots
        instance.generate_slots()


class Material(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.code} - {self.description}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='appointments')
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, related_name='appointments')
    slot = models.OneToOneField('Slot', on_delete=models.CASCADE, related_name='appointment')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    service = models.ManyToManyField(Service, blank=True)
    materials = models.ManyToManyField(Material, blank=True)


    def __str__(self):
        return f"{self.customer.name} - {self.slot}"

    def clean(self):
        if self.slot.is_booked():
            if self.slot.appointment and self.slot.appointment.pk != self.pk:
                raise ValidationError("This slot is already booked.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def date(self):
        return self.slot.date

    @property
    def start_time(self):
        return self.slot.start_time

    class Meta:
        ordering = ['slot__date', 'slot__start_time']

