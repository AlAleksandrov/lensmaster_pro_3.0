from django.contrib import admin
from unfold.admin import ModelAdmin
from bookings.models import ServicePackage, BookingRequest, Availability, BusinessHours


@admin.register(ServicePackage)
class ServicePackageAdmin(ModelAdmin):
    list_display = ('name', 'price', 'duration_hours', 'max_photos_included', 'is_active')
    list_filter = ('is_active', 'duration_hours',)
    search_fields = ('name', 'description')

    fieldsets = (
        ('Package Details', {
            'fields': ('name', 'category', 'description', 'price')
        }),
        ('Service Specifications', {
            'fields': ('duration_hours', 'max_photos_included')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(BookingRequest)
class BookingRequestAdmin(ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email',
        'event_date', 'slot_start_time', 'package',
        'photographer', 'status', 'is_paid', 'created_at',
    )
    list_filter = ('status', 'heard_from', 'is_paid', 'photographer', 'event_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'city', 'message', 'stripe_payment_id')
    readonly_fields = ('created_at', 'updated_at', 'stripe_payment_id')
    list_select_related = ('package', 'photographer')
    date_hierarchy = 'event_date'

    fieldsets = (
        ('Client Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'city')
        }),
        ('Event Details', {
            'fields': ('event_date', 'slot_start_time', 'package', 'photographer', 'message')
        }),
        ('Marketing & Status', {
            'fields': ('heard_from', 'status')
        }),
        ('Payment', {
            'fields': ('is_paid', 'stripe_payment_id'),
        }),
        ('Internal', {
            'fields': ('internal_notes', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Availability)
class AvailabilityAdmin(ModelAdmin):
    list_display = ('photographer', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'photographer')


@admin.register(BusinessHours)
class BusinessHoursAdmin(ModelAdmin):
    list_display = ('day', 'is_working', 'start_time', 'end_time')