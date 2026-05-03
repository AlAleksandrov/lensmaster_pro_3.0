import django_filters

from bookings.models import BookingRequest, ServicePackage


class BookingRequestFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(field_name='event_date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='event_date', lookup_expr='lte')
    name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    full_name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')

    class Meta:
        model = BookingRequest
        fields = {
            'status': ['exact'],
            'package': ['exact'],
            'heard_from': ['exact'],
        }


class ServicePackageFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = ServicePackage
        fields = {
            'category': ['exact'],
            'is_active': ['exact'],
            'duration_hours': ['exact', 'gte', 'lte'],
        }
