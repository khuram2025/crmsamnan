from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from profiles.models import CustomerProfile, TechnicianProfile, ManagerProfile, CallCenterAgentProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'CUSTOMER':
            CustomerProfile.objects.create(user=instance)
        elif instance.role == 'TECHNICIAN':
            TechnicianProfile.objects.create(user=instance)
        elif instance.role == 'MANAGER':
            ManagerProfile.objects.create(user=instance)
        elif instance.role == 'CALL_CENTER_AGENT':
            CallCenterAgentProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'customerprofile'):
        instance.customerprofile.save()
    elif hasattr(instance, 'technicianprofile'):
        instance.technicianprofile.save()
    elif hasattr(instance, 'managerprofile'):
        instance.managerprofile.save()
    elif hasattr(instance, 'callcenteragentprofile'):
        instance.callcenteragentprofile.save()