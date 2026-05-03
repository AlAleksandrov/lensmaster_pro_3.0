from django.urls import path, include
from bookings import views_api


urlpatterns = [
        path('booking-requests/', include([
            path('', views_api.BookingRequestListAPIView.as_view(), name='api_booking_list'),
            path('create/', views_api.BookingRequestCreateAPIView.as_view(), name='api_booking_request'),
        ])),
        path('service-packages/', include([
            path('', views_api.ServicePackageListAPIView.as_view(), name='api_package_list'),
            path('<int:pk>/', views_api.ServicePackageDetailAPIView.as_view(), name='api_package_detail'),
        ])),
        path('available-slots/', views_api.AvailableSlotsAPIView.as_view(), name='api_available_slots'),
]