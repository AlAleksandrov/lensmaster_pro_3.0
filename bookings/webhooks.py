import stripe
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from bookings.models import BookingRequest

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError as e:
        logger.warning("Invalid Stripe signature: %s", e)
        return HttpResponse(status=400)
    except Exception as e:
        logger.error("Webhook general error: %s", e)
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        booking_id = getattr(session, 'client_reference_id', None)
        payment_status = getattr(session, 'payment_status', None)

        if not booking_id:
            logger.warning("Webhook received without client_reference_id")
            return HttpResponse(status=200)

        if payment_status != 'paid':
            logger.warning(
                "Checkout completed but payment_status=%s for booking_id=%s",
                payment_status,
                booking_id,
            )
            return HttpResponse(status=200)

        try:
            booking = BookingRequest.objects.get(id=booking_id)

            if booking.is_paid and booking.status == BookingRequest.Status.CONFIRMED:
                logger.info(
                    "Webhook duplicate ignored for booking_id=%s already confirmed",
                    booking_id,
                )
                return HttpResponse(status=200)

            booking.is_paid = True
            booking.status = BookingRequest.Status.CONFIRMED
            booking.save(update_fields=['is_paid', 'status'])

            logger.info("Booking id=%s confirmed via Stripe webhook", booking_id)

        except BookingRequest.DoesNotExist:
            logger.warning(
                "BookingRequest with id=%s does not exist webhook",
                booking_id,
            )

    return HttpResponse(status=200)