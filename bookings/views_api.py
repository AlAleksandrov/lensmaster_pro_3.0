from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from bookings.filters import BookingRequestFilter, ServicePackageFilter
from bookings.models import ServicePackage, BookingRequest
from bookings.serializers import ServicePackageSerializer, BookingRequestSerializer
from bookings.services.availability import get_available_slots
from django.utils import timezone


class ServicePackageListAPIView(ListAPIView):
    queryset = ServicePackage.objects.filter(is_active=True)
    serializer_class = ServicePackageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ServicePackageFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'duration_hours']
    permission_classes = [IsAuthenticatedOrReadOnly]


class ServicePackageDetailAPIView(RetrieveAPIView):
    queryset = ServicePackage.objects.filter(is_active=True)
    serializer_class = ServicePackageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookingRequestCreateAPIView(CreateAPIView):
    queryset = BookingRequest.objects.all()
    serializer_class = BookingRequestSerializer
    permission_classes = [IsAuthenticated]


class BookingRequestListAPIView(ListAPIView):
    serializer_class = BookingRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = BookingRequestFilter
    search_fields = ['first_name', 'last_name', 'email']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.groups.filter(name='Photographers').exists():
            return BookingRequest.objects.all()

        return BookingRequest.objects.filter(user=user)


class AvailableSlotsAPIView(APIView):

    def get(self, request):
        date_str = request.GET.get('date')
        photographer_id = request.GET.get('photographer')
        package_id = request.GET.get('package')

        if not date_str:
            return Response({'error': 'date is required'}, status=400)



        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            if date < timezone.now().date():
                return Response({'error': 'Cannot check availability for past dates.'}, status=400)

        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        photographer = None
        if photographer_id:
            User = get_user_model()
            photographer = get_object_or_404(User, id=photographer_id)

        package = None
        if package_id:
            package = get_object_or_404(ServicePackage, id=package_id)

        slots = get_available_slots(date, photographer, package)

        return Response(slots)