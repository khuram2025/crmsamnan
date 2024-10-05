from django.db import models
from profiles.models import TechnicianProfile
from datetime import timedelta, date
from django.utils import timezone

from django.db import models
from profiles.models import TechnicianProfile
from datetime import timedelta, datetime
from django.utils import timezone


class Shift(models.Model):
    SHIFT_CHOICES = (
        ('MORNING', 'Morning'),
        ('EVENING', 'Evening'),
    )
    name = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


class WorkingSlot(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    gap_between_slots = models.DurationField(default=timedelta(minutes=0), help_text="Optional gap between slots.")

    def __str__(self):
        return f"Slot from {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')} in {self.shift.name}"

    @classmethod
    def create_slots(cls, shift, duration, gap=timedelta(minutes=0)):
        """Automatically create slots within the shift based on the given duration and optional gap."""
        current_start_time = shift.start_time
        slots = []

        while datetime.combine(datetime.today(), current_start_time) + duration <= datetime.combine(datetime.today(), shift.end_time):
            current_end_time = (datetime.combine(datetime.today(), current_start_time) + duration).time()

            slots.append(cls(shift=shift, start_time=current_start_time, end_time=current_end_time))
            
            # Increment start time by the slot duration and the optional gap
            current_start_time = (datetime.combine(datetime.today(), current_end_time) + gap).time()

        return slots


class TechnicianAvailability(models.Model):
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE)
    date = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    slot = models.ForeignKey(WorkingSlot, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('technician', 'date', 'shift', 'slot')

    def __str__(self):
        return f'{self.technician.user.email} on {self.date} during {self.slot}'
