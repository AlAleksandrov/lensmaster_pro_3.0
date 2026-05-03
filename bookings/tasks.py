import logging
import smtplib
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from bookings.models import BookingRequest

try:
    from django_q.tasks import async_task
except ImportError:
    async_task = None


logger = logging.getLogger(__name__)


def _send_booking_confirmation_email(booking_id):
    try:
        booking = BookingRequest.objects.select_related("package").get(pk=booking_id)
    except BookingRequest.DoesNotExist:
        logger.warning("BookingRequest with id=%s does not exist. Email not sent.", booking_id)
        return False

    subject = "Booking Confirmed! - LensMaster Pro"
    message = (
        f"Dear {booking.full_name},\n\n"
        f"Great news! Your booking has been CONFIRMED.\n\n"
        f"📋 Booking Details:\n"
        f"  • Booking ID: #{booking_id}\n"
        f"  • Package: {booking.package.name if booking.package else 'N/A'}\n"
        f"  • Event Date: {booking.event_date}\n"
        f"  • Duration: {booking.package.duration_hours if booking.package else 'N/A'} hours\n\n"
        f"If you have any questions, please reply to this email.\n\n"
        f"Thank you for choosing LensMaster Pro!\n"
        f"Best regards,\n"
        f"The LensMaster Pro Team"
    )

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if not from_email:
        logger.error(
            "DEFAULT_FROM_EMAIL is not configured. Booking confirmation email not sent for booking_id=%s",
            booking_id,
        )
        return False

    email_host = getattr(settings, "EMAIL_HOST", "")
    email_user = getattr(settings, "EMAIL_HOST_USER", "")
    email_password = getattr(settings, "EMAIL_HOST_PASSWORD", "")

    if not email_host or not email_user or not email_password:
        logger.error(
            "Email settings are incomplete (EMAIL_HOST / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD). "
            "Booking confirmation email not sent for booking_id=%s",
            booking_id,
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[booking.email],
            fail_silently=False,
        )
        logger.info("Booking confirmation email sent successfully for booking_id=%s", booking_id)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.exception(
            "SMTP authentication failed while sending booking confirmation email for booking_id=%s. "
            "Check your Mailjet SMTP credentials and verified sender/domain.",
            booking_id,
        )
        return False

    except Exception:
        logger.exception(
            "Unexpected error while sending booking confirmation email for booking_id=%s",
            booking_id,
        )
        return False


def dispatch_booking_confirmation(booking_id):
    from django.conf import settings
    async_backend = getattr(settings, "ASYNC_TASK_BACKEND", "django_q")

    try:
        if async_backend == "celery":
            send_booking_confirmation_celery.delay(booking_id)
            logger.info("Celery task queued for booking_id=%s", booking_id)
        else:
            if async_task is None:
                logger.error(
                    "django_q not installed but ASYNC_TASK_BACKEND=django_q. "
                    "Falling back to sync send for booking_id=%s", booking_id
                )
                _send_booking_confirmation_email(booking_id)
                return
            async_task(
                "bookings.tasks._send_booking_confirmation_email",
                booking_id,
            )
            logger.info("django_q task queued for booking_id=%s", booking_id)
    except Exception:
        logger.exception(
            "Failed to dispatch confirmation email for booking_id=%s. "
            "Attempting sync fallback.", booking_id
        )
        _send_booking_confirmation_email(booking_id)


def send_booking_confirmation(booking_id):
    dispatch_booking_confirmation(booking_id)


@shared_task
def send_booking_confirmation_celery(booking_id):
    return _send_booking_confirmation_email(booking_id)