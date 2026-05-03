from datetime import datetime, timedelta
from bookings.models import Availability, BookingRequest


def get_available_slots(date, photographer=None, package=None):
    day_of_week = date.weekday()
    slot_duration_hours = package.duration_hours if package else 1

    availabilities = Availability.objects.filter(day_of_week=day_of_week)

    if photographer:
        availabilities = availabilities.filter(photographer=photographer)

    slots = []

    for availability in availabilities:
        current_time = availability.start_time

        while True:
            end_time = (
                datetime.combine(date, current_time)
                + timedelta(hours=slot_duration_hours)
            ).time()

            if end_time > availability.end_time:
                break

            is_taken = BookingRequest.objects.filter(
                photographer=availability.photographer,
                event_date=date,
                status__in=[
                    BookingRequest.Status.PENDING,
                    BookingRequest.Status.CONFIRMED,
                ],
                slot_start_time__lt=end_time,
                slot_start_time__gte=current_time,
            ).exists()

            if not is_taken:
                slots.append({
                    'photographer_id': availability.photographer.id,
                    'photographer_name': availability.photographer.get_full_name(),
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': end_time.strftime('%H:%M'),
                    'duration_hours': slot_duration_hours,
                })

            current_time = end_time

    return slots