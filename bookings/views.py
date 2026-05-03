import logging
import stripe
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.core.exceptions import PermissionDenied
from bookings.forms import BookingRequestForm, ServicePackageForm
from bookings.models import BookingRequest, ServicePackage
from django.db.models import Q
from common.mixins import PhotographerRequiredMixin


stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

# Create your views here.
class BookingCreateView(CreateView):
    model = BookingRequest
    form_class = BookingRequestForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:booking_success')

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            initial['first_name'] = getattr(user, 'first_name', '')
            initial['last_name'] = getattr(user, 'last_name', '')
            initial['email'] = getattr(user, 'email', '')

            try:
                if hasattr(user, 'profile'):
                    initial['phone'] = user.profile.phone
                    initial['city'] = user.profile.city
            except Exception:
                pass
        return initial

    def form_valid(self, form):
        booking = form.save(commit=False)

        if self.request.user.is_authenticated:
            booking.user = self.request.user

        if not booking.package:
            booking.save()
            return redirect(self.success_url)

        booking.save()

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=form.cleaned_data.get('email'),
                customer_creation='always',
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f"Package: {booking.package.name}",
                            'description': (
                                f"Date: {booking.event_date} | "
                                f"Client: {form.cleaned_data.get('first_name')} "
                                f"{form.cleaned_data.get('last_name')}"
                            ),
                        },
                        'unit_amount': int(booking.package.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                payment_intent_data={
                    'description': f"Booking #{booking.id} — {booking.package.name}",
                },
                metadata={
                    'booking_id': str(booking.id),
                    'package_id': str(booking.package.id),
                    'customer_email': form.cleaned_data.get('email', ''),
                },
                success_url=str(self.request.build_absolute_uri(
                    reverse_lazy('bookings:booking_success')
                )),
                cancel_url=str(self.request.build_absolute_uri(
                    reverse_lazy('bookings:booking_request')
                )),
                client_reference_id=str(booking.id),
            )

            booking.stripe_payment_id = session.id
            booking.save(update_fields=['stripe_payment_id'])

            return redirect(session.url, code=303)

        except stripe.error.StripeError as e:
            logger.error("Stripe error for booking id=%s: %s", booking.id, e)
            booking.delete()
            form.add_error(None, "Payment service is temporarily unavailable. Please try again.")
            return self.form_invalid(form)

        except Exception as e:
            logger.exception("Unexpected error during booking creation for id=%s: %s", booking.id, e)
            booking.delete()
            form.add_error(None, "An unexpected error occurred. Please try again.")
            return self.form_invalid(form)

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        package_id = self.request.GET.get('package')
        if package_id:
            form.fields['package'].initial = package_id
        return form


class BookingListView(PhotographerRequiredMixin, ListView):
    model = BookingRequest
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 3

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.GET.get('status', '').strip()
        q = self.request.GET.get('q', '').strip()

        if status:
            qs = qs.filter(status=status)

        if q:
            qs = qs.filter(
                Q(first_name__icontains=q)
                    |
                Q(last_name__icontains=q)
                    |
                Q(email__icontains=q)
                    |
                Q(phone__icontains=q)

            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = BookingRequest.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class BookingUpdateView(PhotographerRequiredMixin, UpdateView):
    model = BookingRequest
    fields = ['status', 'internal_notes', 'event_date', 'package', 'photographer', 'slot_start_time', 'is_paid']
    template_name = 'bookings/booking_edit.html'
    success_url = reverse_lazy('bookings:booking_list')


class BookingDeleteView(PhotographerRequiredMixin, DeleteView):
    model = BookingRequest
    template_name = 'bookings/booking_confirm_delete.html'
    success_url = reverse_lazy('bookings:booking_list')


class ServicePackageListView(ListView):
    model = ServicePackage
    template_name = 'bookings/package_list.html'
    context_object_name = 'packages'
    paginate_by = 5

    def get_queryset(self):
        qs = super().get_queryset().order_by('category__name', 'price')
        user = self.request.user
        if not (user.is_superuser or (user.is_authenticated and user.groups.filter(name='Photographers').exists())):
            qs = qs.filter(is_active=True)
        return qs

    def get_context_data(self, *, object_list = ..., **kwargs):
        context = super().get_context_data(**kwargs)
        context['package_create_url'] = reverse_lazy('bookings:package_create')
        return context


class ServicePackageDetailView(DetailView):
    model = ServicePackage
    template_name = 'bookings/package_detail.html'
    context_object_name = 'package'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        is_staff = user.is_superuser or (user.is_authenticated and user.groups.filter(name='Photographers').exists())
        if not obj.is_active and not is_staff:
            raise PermissionDenied
        return obj


class ServicePackageCreateView(PhotographerRequiredMixin, CreateView):
    model = ServicePackage
    form_class = ServicePackageForm
    template_name = 'bookings/package_form.html'
    success_url = reverse_lazy('bookings:package_list')


class ServicePackageUpdateView(PhotographerRequiredMixin, UpdateView):
    model = ServicePackage
    form_class = ServicePackageForm
    template_name = 'bookings/package_form.html'
    success_url = reverse_lazy('bookings:package_list')


class ServicePackageDeleteView(PhotographerRequiredMixin, DeleteView):
    model = ServicePackage
    template_name = 'bookings/package_confirm_delete.html'
    success_url = reverse_lazy('bookings:package_list')


class ServicePackageByCategoryListView(ListView):
    model = ServicePackage
    template_name = 'bookings/package_list_by_category.html'
    context_object_name = 'packages'
    paginate_by = 2

    def get_queryset(self):
        qs = ServicePackage.objects.filter(category_id=self.kwargs['category_id']).order_by('price')
        user = self.request.user
        if not (user.is_superuser or (user.is_authenticated and user.groups.filter(name='Photographers').exists())):
            qs = qs.filter(is_active=True)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.shortcuts import get_object_or_404
        from productions.models import Category
        category = get_object_or_404(Category, pk=self.kwargs['category_id'])
        context['current_category'] = category.name
        return context


class ToggleFavoritePackageView(LoginRequiredMixin, View):
    def post(self, request, pk):
        package = get_object_or_404(ServicePackage, pk=pk)
        profile = getattr(request.user, 'profile', None)

        if profile is None:
            from django.contrib import messages
            messages.warning(request, "Please complete your profile first.")
            return redirect('bookings:package_detail', pk=pk)

        if package in profile.favorite_packages.all():
            profile.favorite_packages.remove(package)
        else:
            profile.favorite_packages.add(package)

        return redirect('bookings:package_detail', pk=pk)