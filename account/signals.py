from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()
from django.db import transaction

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            Profile = apps.get_model('account', 'Profile')
            Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile = apps.get_model('account', 'Profile')  # ✅ Lazy load
    instance.profile.save()
