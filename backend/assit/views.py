from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from booking.models import Bookable


class IndexView(TemplateView):
    template_name = "index_guest.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context['service_list'] = Bookable.objects.all()
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(reverse('service_list'))
        return super().dispatch(request, *args, **kwargs)
