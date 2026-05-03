import logging
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from accounts.models import Profile, User
from bookings.models import BookingRequest

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

        client_group, _ = Group.objects.get_or_create(name='Clients')
        instance.groups.add(client_group)

        if instance.email and instance.first_name and instance.last_name:
            BookingRequest.objects.filter(
                user__isnull=True,
                email__iexact=instance.email,
                first_name__iexact=instance.first_name,
                last_name__iexact=instance.last_name,
            ).update(user=instance)

@receiver(pre_save, sender=BookingRequest)
def handle_booking_request_save(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = BookingRequest.objects.get(pk=instance.pk)
    except BookingRequest.DoesNotExist:
        return

    status_changed_to_confirmed = (
        old_instance.status != BookingRequest.Status.CONFIRMED
        and instance.status == BookingRequest.Status.CONFIRMED
    )

    if not status_changed_to_confirmed:
        return

    booking_id = instance.pk

    def enqueue_task():
        try:
            from bookings.tasks import dispatch_booking_confirmation
            dispatch_booking_confirmation(booking_id)
        except Exception:
            logger.exception(
                "Could not enqueue booking confirmation task for BookingRequest id=%s",
                booking_id,
            )

    transaction.on_commit(enqueue_task)