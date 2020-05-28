from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


USER_MODEL = get_user_model()


PHONE_NUMBER_VALIDATOR = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class UserProfile(models.Model):
    user = models.OneToOneField(USER_MODEL, related_name="profile", on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone_number = models.CharField(
        max_length=17, validators=[PHONE_NUMBER_VALIDATOR], null=True, blank=True
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    is_worker = models.BooleanField(default=False)


@receiver(post_save, sender=USER_MODEL)
def post_save_userprofile(sender, instance, created, *args, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
