from django.urls import path, include
from django.views.generic import TemplateView
from bookings import views
from bookings.webhooks import stripe_webhook

app_name = 'bookings'

service_package_patterns = [
    path('', views.ServicePackageListView.as_view(), name='package_list'),
    path('create/', views.ServicePackageCreateView.as_view(), name='package_create'),
    path('by_category/<int:category_id>/', views.ServicePackageByCategoryListView.as_view(), name='package_list_by_category'),
    path('<int:pk>/', include([
        path('', views.ServicePackageDetailView.as_view(), name='package_detail'),
        path('edit/', views.ServicePackageUpdateView.as_view(), name='package_edit'),
        path('delete/', views.ServicePackageDeleteView.as_view(), name='package_delete'),
        ]),
    ),
]

urlpatterns = [
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('api/', include('bookings.urls_api')),
    path('package/<int:pk>/favorite/', views.ToggleFavoritePackageView.as_view(), name='toggle_favorite_package'),
    path('request/', views.BookingCreateView.as_view(), name='booking_request'),
    path('success/', TemplateView.as_view(template_name='bookings/booking_success.html'), name='booking_success'),
    path('packages/', include(service_package_patterns)),
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('<int:pk>/', include([
        path('edit/', views.BookingUpdateView.as_view(), name='booking_edit'),
        path('delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
        ]),
    ),
]
