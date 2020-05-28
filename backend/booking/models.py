from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from model_utils.models import TimeStampedModel

from .utils import get_compressed_image


USER_MODEL = get_user_model()


class Bookable(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True, default=None)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)

    days_available = models.CharField(max_length=255)
    hour_start = models.TimeField()
    hour_end = models.TimeField()

    def get_available_days(self):
        return self.days_available.split('|')

    def save(self, *args, **kwargs):
        if self.thumbnail:
            self.thumbnail = get_compressed_image(self.thumbnail, (1120, 540))
        super(Bookable, self).save()

    class Meta:
        permissions = [
            ("manage", "Can create/edit/delete a bookable and inputs.")
        ]


@receiver(pre_save, sender=Bookable)
def pre_save_bookable(sender, instance, *args, **kwargs):
    if not instance.slug:
        new_slug = slugify(instance.name)
        counter = 2
        while Bookable.objects.filter(slug=new_slug).exists():
            new_slug = new_slug + "-{0}".format(counter)
            counter += 1
        instance.slug = new_slug


class BookableInput(TimeStampedModel):
    FIELD_TYPE_TEXT = "ft_text"
    FIELD_TYPE_TEXT_MULTILINE = "ft_text_multiline"
    FIELD_TYPE_DATE = "ft_date"
    FIELD_TYPE_TIME = "ft_time"
    FIELD_TYPE_CHECKBOX = "ft_checkbox"
    FIELD_TYPE_CHOICES = [
        (FIELD_TYPE_TEXT, "Text"),
        (FIELD_TYPE_TEXT_MULTILINE, "Text multi-line"),
        (FIELD_TYPE_DATE, "Date"),
        (FIELD_TYPE_TIME, "Time"),
        (FIELD_TYPE_CHECKBOX, "Checkbox")
    ]

    bookable = models.ForeignKey(Bookable, related_name="inputs", on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    field_type = models.CharField(
        max_length=25, default=FIELD_TYPE_TEXT, choices=FIELD_TYPE_CHOICES
    )
    field_required = models.BooleanField(default=False)


class BookedService(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    PAYMENT_STATUS_CHOICES = [
        (STATUS_PENDING, 'Payment pending'),
        (STATUS_COMPLETED, 'Payment completed')
    ]

    user = models.ForeignKey(USER_MODEL, related_name="booked_services", on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    name = models.CharField(max_length=255)
    summary = models.TextField()
    confirmed = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=15, default=STATUS_PENDING, choices=PAYMENT_STATUS_CHOICES
    )
    assigned_worker = models.ForeignKey(
        USER_MODEL,
        related_name="assigned_booked_services",
        on_delete=models.CASCADE, null=True,
        blank=True
    )
    stripe_session_id = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['-created']
