from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, UserRole
from apps.core.choices import AppRole

User = get_user_model()


@receiver(post_save, sender=User)
def handle_new_user(sender, instance, created, **kwargs):

    if created:

        Profile.objects.create(
            user=instance,
            email=instance.email,
            full_name=instance.username
        )

        UserRole.objects.create(
            user=instance,
            role=AppRole.USER
        )
