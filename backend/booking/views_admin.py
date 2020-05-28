import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    DeleteView, FormView, ListView, TemplateView, UpdateView, CreateView)

from users.models import UserProfile
from users.utils import user_has_completed_profile

from .forms import (ServiceCreateForm, ServiceUpdateForm, WorkerCreateForm,
                    WorkerDeleteForm)
from .models import Bookable, BookableInput, BookedService

USER_MODEL = get_user_model()


class BookableList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "manage/bookable_list.html"
    model = Bookable
    permission_required = "booking.manage"


class BookableCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "manage/bookable_create.html"
    form_class = ServiceCreateForm
    success_url = reverse_lazy('manage_bookable_list')
    success_message = "The new service was created successfully!"
    permission_required = "booking.manage"

    def form_valid(self, form):
        form_data = form.cleaned_data

        if Bookable.objects.filter(name=form_data.get('name')).exists():
            form.add_error('name', ValidationError(
                f"A service with the same name already exists. Please choose another name."
            ))
            return super().form_invalid(form)

        price = form_data.get('price')

        if price < 1:
            form.add_error('price', ValidationError(
                f"The price must be greater than $1"
            ))
            return super().form_invalid(form)

        bookable = Bookable.objects.create(
            name=form_data.get('name'),
            description=form_data.get('description'),
            price=price,
            unit=form_data.get('unit'),
            thumbnail=form_data.get('thumbnail'),
            days_available='|'.join(form_data.get('available_days')),
            hour_start=form_data.get('hour_start'),
            hour_end=form_data.get('hour_end')
        )

        try:
            custom_inputs = json.loads(form_data.get('custom_inputs'))
        except:
            custom_inputs = None

        if custom_inputs is not None:
            for custom_input in custom_inputs:
                BookableInput.objects.create(
                    bookable=bookable,
                    label=custom_input["label"],
                    field_type=custom_input["field_type"],
                    field_required=custom_input["field_required"]
                )

        messages.success(self.request, "Successfully created a new Service!")
        return super().form_valid(form)


class BookableUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "manage/bookable_update.html"
    model = Bookable
    form_class = ServiceUpdateForm
    success_url = reverse_lazy('manage_bookable_list')
    success_message = "The service was updated successfully!"
    permission_required = "booking.manage"

    def form_valid(self, form):
        form.instance.days_available = '|'.join(form.cleaned_data.get('available_days'))
        return super().form_valid(form)


class BookableInputListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "manage/bookable_input_list.html"
    model = BookableInput
    permission_required = "booking.manage"

    def get_context_data(self, **kwargs):
        bookable_slug = self.kwargs.get('slug')
        bookable = Bookable.objects.get(slug=bookable_slug)
        context = super().get_context_data(**kwargs)
        context["bookable"] = bookable
        return context

    def get_queryset(self):
        bookable_slug = self.kwargs.get('slug')
        queryset = BookableInput.objects.filter(bookable__slug=bookable_slug)
        return queryset


class BookableInputCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = "manage/bookable_input_create.html"
    model = BookableInput
    fields = ['label', 'field_type', 'field_required']
    success_message = "The input was created successfully."
    permission_required = "booking.manage"

    def get_success_url(self):
        slug = self.kwargs.get('slug')
        return reverse_lazy("manage_bookable_input_list", kwargs={'slug': slug})

    def form_valid(self, form):
        bookable_slug = self.kwargs.get('slug')
        bookable = Bookable.objects.get(slug=bookable_slug)
        form.instance.bookable = bookable
        print(bookable)
        return super().form_valid(form)


class BookableInputDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    template_name = "manage/bookable_input_delete.html"
    model = BookableInput
    success_message = "The input was deleted successfully."
    permission_required = "booking.manage"

    def get_success_url(self):
        slug = self.kwargs.get('slug')
        return reverse_lazy("manage_bookable_input_list", kwargs={'slug': slug})

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class BookableDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    template_name = "manage/bookable_delete.html"
    model = Bookable
    success_url = reverse_lazy("manage_bookable_list")
    success_message = "The service was deleted successfully."
    permission_required = "booking.manage"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class BookedServiceAssignWorker(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "manage/booked_service_assign_worker.html"
    model = BookedService
    fields = ['assigned_worker']
    permission_required = "booking.manage"
    success_url = reverse_lazy("manage_booked_services")
    success_message = "Assigned the worker successfully!"

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["assigned_worker"].queryset = USER_MODEL.objects.filter(profile__is_worker=True)
        return form


class AdminBookedServiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "manage/booked_service_list.html"
    model = BookedService
    permission_required = "booking.manage"


class WorkerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "manage/worker_list.html"
    model = USER_MODEL
    permission_required = "booking.manage"

    def get_queryset(self):
        return USER_MODEL.objects.filter(profile__is_worker=True)


class WorkerCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "manage/worker_create.html"
    form_class = WorkerCreateForm
    success_url = reverse_lazy("manage_worker_list")
    permission_required = "booking.manage"

    def form_valid(self, form):
        selected_user = form.cleaned_data["user"]
        if not user_has_completed_profile(selected_user):
            form.add_error('user', ValidationError(
                f'The selected user did not complete his Profile. You cannot make him a worker.'
            ))
            return super().form_invalid(form)

        user_profile = selected_user.profile
        user_profile.is_worker = True
        user_profile.save()

        messages.success(self.request, "Successfully added a new worker!")
        return super().form_valid(form)


class WorkerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "manage/worker_delete.html"
    form_class = WorkerDeleteForm
    success_url = reverse_lazy("manage_worker_list")
    permission_required = "booking.manage"

    def form_valid(self, form):
        selected_user = form.cleaned_data["worker"]
        user_profile = selected_user.profile
        user_profile.is_worker = False
        user_profile.save()

        messages.success(self.request, "Successfully removed the worker.")
        return super().form_valid(form)
