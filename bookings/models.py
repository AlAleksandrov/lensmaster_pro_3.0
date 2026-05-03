from django.conf import settings
from django.db import models
from django.utils import timezone

from common.models import DescriptionMixin, ActiveStatusMixin, TimestampedMixin, ContactInfoMixin
from django.core.exceptions import ValidationError


# Create your models here.
class BusinessHours(models.Model):
    class Day(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    day = models.IntegerField(
        choices=Day.choices,
        unique=True,
    )

    is_working = models.BooleanField(
        default=True,
    )

    start_time = models.TimeField(
        default="10:00",
    )

    end_time = models.TimeField(
        default="22:00",
    )

    class Meta:
        ordering = ['day']

    def __str__(self):
        status = "Open" if self.is_working else "Closed"
        return f"{self.get_day_display()}: {status} ({self.start_time}-{self.end_time})"

class ServicePackage(DescriptionMixin, ActiveStatusMixin, models.Model):
    name = models.CharField(
        max_length=120,
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    duration_hours = models.PositiveIntegerField(
        default=8,
        help_text='Typical coverage duration in hours.',
    )

    max_photos_included = models.PositiveIntegerField(
        default=200,
        help_text='Approximate number of edited photos included.',
    )

    category = models.ForeignKey(
        'productions.Category',
        on_delete=models.SET_NULL,
        related_name='packages',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f'{self.name} - €{self.price} per {self.duration_hours} hours'


class BookingRequest(TimestampedMixin, ContactInfoMixin, models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    class Source(models.TextChoices):
        FACEBOOK = 'facebook', 'Facebook'
        INSTAGRAM = 'instagram', 'Instagram'
        GOOGLE = 'google', 'Google search'
        FRIEND = 'friend', 'Friend referral'
        OTHER = 'other', 'Other'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
    )

    first_name = models.CharField(
        max_length=50,
    )

    last_name = models.CharField(
        max_length=50,
    )

    email = models.EmailField()

    event_date = models.DateField()

    package = models.ForeignKey(
        'ServicePackage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
    )

    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bookings',
    )

    message = models.TextField(
        blank=True,
    )

    heard_from = models.CharField(
        max_length=20,
        choices=Source,
        default=Source.OTHER,
        help_text='Where did you hear about us?',
    )

    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
    )

    internal_notes = models.TextField(
        blank=True,
        help_text='Internal notes visible only in the admin area.',
    )

    stripe_payment_id = models.CharField(
        max_length=255, blank=True, null=True,
    )

    is_paid = models.BooleanField(
        default=False,
    )

    slot_start_time = models.TimeField(
        null=True, blank=True,
    )

    class Meta:
        ordering = ['-created_at']

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def clean(self):
        if self.event_date and self.event_date < timezone.now().date():
            raise ValidationError({'event_date': 'Event date cannot be in the past.'})

    def __str__(self):
        return f'{self.full_name} - {self.event_date} ({self.get_status_display()})'


class Availability(models.Model):
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities',
    )
    day_of_week = models.IntegerField(
        choices=BusinessHours.Day.choices,
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['photographer', 'day_of_week', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['photographer', 'day_of_week', 'start_time', 'end_time'],
                name='unique_photographer_availability_slot',
            ),
        ]

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Start time must be earlier than end time.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'{self.photographer} - '
            f'{self.get_day_of_week_display()} '
            f'({self.start_time}-{self.end_time})'
        )
