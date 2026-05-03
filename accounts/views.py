from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from accounts.forms import UserRegisterForm, ProfileEditForm
from accounts.models import Profile
from bookings.models import BookingRequest, ServicePackage
from inventory.models import Equipment
from productions.models import Production, Category

User = get_user_model()

# Create your views here.
class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.email and user.first_name and user.last_name:
            BookingRequest.objects.filter(
                user__isnull=True,
                email__iexact=user.email,
                first_name__iexact=user.first_name,
                last_name__iexact=user.last_name,
            ).update(user=user)

        context['bookings'] = BookingRequest.objects.filter(
            user=user,
        ).order_by('-event_date')

        context['favorite_productions'] = self.object.favorite_productions.all()
        context['favorite_equipment'] = self.object.favorite_equipment.all()
        context['favorite_packages'] = self.object.favorite_packages.all()

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile_detail')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class StatsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/stats.html'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name='Photographers').exists()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['top_productions'] = (
            Production.objects
            .annotate(fav_count=Count('favorite_by'))
            .filter(fav_count__gt=0)
            .order_by('-fav_count')[:10]
        )

        ctx['top_equipment_fav'] = (
            Equipment.objects
            .annotate(fav_count=Count('favorite_by'))
            .filter(fav_count__gt=0)
            .order_by('-fav_count')[:10]
        )

        ctx['top_equipment_used'] = (
            Equipment.objects
            .annotate(used_count=Count('productions'))
            .filter(used_count__gt=0)
            .order_by('-used_count')[:10]
        )

        ctx['top_packages_fav'] = (
            ServicePackage.objects
            .annotate(fav_count=Count('favorite_by'))
            .filter(fav_count__gt=0)
            .order_by('-fav_count')[:10]
        )

        ctx['top_packages_booked'] = (
            ServicePackage.objects
            .annotate(booking_count=Count('bookings'))
            .filter(booking_count__gt=0)
            .order_by('-booking_count')[:10]
        )

        ctx['bookings_by_status'] = (
            BookingRequest.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        ctx['bookings_by_source'] = (
            BookingRequest.objects
            .values('heard_from')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        ctx['categories_by_productions'] = (

            Category.objects
            .annotate(prod_count=Count('productions'))
            .order_by('-prod_count')
        )

        ctx['total_productions'] = Production.objects.count()
        ctx['total_equipment'] = Equipment.objects.count()
        ctx['total_packages'] = ServicePackage.objects.count()
        ctx['total_bookings'] = BookingRequest.objects.count()
        ctx['confirmed_bookings'] = BookingRequest.objects.filter(status='confirmed').count()

        return ctx