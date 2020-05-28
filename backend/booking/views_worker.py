from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import BookedService
from django.core.exceptions import PermissionDenied


class WorkerPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.user_has_permissions(request):
            return super(WorkerPermissionMixin, self).dispatch(
                request, *args, **kwargs)
        else:
            raise PermissionDenied

    def user_has_permissions(self, request):
        if self.request.user.profile.is_worker:
            return True
        return False


class WorkerDashboardView(LoginRequiredMixin, WorkerPermissionMixin, ListView):
    template_name = "workers/dashboard.html"
    model = BookedService

    def get_queryset(self):
        return BookedService.objects.filter(assigned_worker=self.request.user)
