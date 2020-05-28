from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import UserProfile

from booking.models import BookedService


class UserProfileObjectMixin():
    def get_object(self):
        return self.request.user.profile


class ProfileDetailView(LoginRequiredMixin, SuccessMessageMixin, UserProfileObjectMixin, DetailView):
    template_name = "users/profile_detail.html"
    model = UserProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booked_services"] = BookedService.objects.filter(user=self.request.user)
        return context


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UserProfileObjectMixin, UpdateView):
    template_name = "users/profile_update.html"
    model = UserProfile
    fields = ['avatar', 'name', 'phone_number']
    success_url = reverse_lazy('users_profile')
    success_message = 'Your profile was updated successfully!'
