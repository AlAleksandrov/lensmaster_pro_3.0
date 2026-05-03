from rest_framework import serializers
from bookings.models import ServicePackage, BookingRequest


class ServicePackageSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = ServicePackage
        fields = [
            'id',
            'name',
            'description',
            'price',
            'duration_hours',
            'max_photos_included',
            'category',
            'category_name',
            'is_active',
        ]


class BookingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'email',
            'event_date',
            'package',
            'message',
            'heard_from',
            'status',
        ]
        read_only_fields = ['status', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)
