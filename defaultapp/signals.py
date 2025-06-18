from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver

from defaultapp.models import Profile


@receiver(post_save, sender=User)
def add_to_common_user_group(sender, instance, created, **kwargs):
    if created:
        common_user_group, created_group = Group.objects.get_or_create(name='Common user')
        instance.groups.add(common_user_group)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)

