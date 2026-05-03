from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class TimestampedMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True


class SlugMixin(models.Model):
    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            source = getattr(self, 'name', getattr(self, 'title', 'item'))
            self.slug = slugify(source)

        super().save(*args, **kwargs)


class DescriptionMixin(models.Model):
    description = models.TextField(
        blank=True,
    )

    class Meta:
        abstract = True


class ActiveStatusMixin(models.Model):
    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this item without deleting it',
    )

    class Meta:
        abstract = True


class ContactInfoMixin(models.Model):
    phone = PhoneNumberField(
        blank=False,
        null=False,
        help_text="Enter phone number with country code for contact purposes"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='City for contact purposes',
    )

    class Meta:
        abstract = True