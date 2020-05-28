import datetime
from urllib.parse import urljoin

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, ListView, TemplateView

from users.utils import user_has_completed_profile

from .forms import CustomForm
from .models import Bookable, BookedService
from .utils import is_time_between

stripe.api_key = settings.STRIPE_API_KEY

TIME_FORMAT = settings.TIME_FORMAT


class PublicServiceListView(ListView):
    template_name = "public_service_list.html"
    model = Bookable
    paginate_by = 20


class ServiceListView(ListView):
    template_name = "service_list.html"
    model = Bookable


class ServiceBookingView(FormView):
    template_name = "service_detail.html"
    form_class = CustomForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context["bookable"] = Bookable.objects.get(slug=slug)
        return context

    def get_form_kwargs(self):
        slug = self.kwargs.get('slug')
        if slug is None:
            raise ValidationError("Bad request")
        try:
            bookable = Bookable.objects.get(slug=slug)
        except Bookable.DoesNotExist:
            raise ValidationError("Bad request")
        kwargs = super().get_form_kwargs()
        kwargs['custom_inputs'] = bookable.inputs.all()
        kwargs['bookable'] = bookable
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Please register for an account to complete your booking")
            return HttpResponseRedirect('/accounts/login/')

        if not user_has_completed_profile(self.request.user):
            messages.error(self.request, "You must complete your Profile before booking a service.")
            return HttpResponseRedirect(reverse('users_profile_update'))

        slug = self.kwargs.get('slug')
        bookable = Bookable.objects.get(slug=slug)

        selected_date = form.cleaned_data.get("selected_date")
        selected_time = form.cleaned_data.get("selected_time")

        throw_error = False

        if not selected_date.strftime("%a").lower() in bookable.get_available_days():
            form.add_error('selected_date', ValidationError(
                f"The date that you selected is not available."
            ))
            throw_error = True

        if selected_date < datetime.datetime.now().date():
            form.add_error('selected_date', ValidationError(
                f'The selected date must be in the future.'
            ))
            throw_error = True

        selected_time.replace(tzinfo=None)
        hour_start = bookable.hour_start.replace(tzinfo=None)
        hour_end = bookable.hour_end.replace(tzinfo=None)

        if not is_time_between(hour_start, hour_end, selected_time):
            hour_start = bookable.hour_start.strftime(TIME_FORMAT)
            hour_end = bookable.hour_end.strftime(TIME_FORMAT)
            form.add_error('selected_time', ValidationError(
                f"The selected time must be between {hour_start} and {hour_end}"
            ))
            throw_error = True

        if throw_error:
            return super().form_invalid(form)

        quantity = form.cleaned_data.get("quantity")

        summary = (
            f"Description: {bookable.description}, \n" +
            f"Price per unit: {bookable.price}, \n"
        )
        for name, value in form.cleaned_data.items():
            summary += f"{form.fields[name].label} - {value}, \n"
        summary = summary[:-2]

        item = {
            'name': bookable.name,
            'description': summary,
            'amount': int(bookable.price) * 100,
            'currency': 'usd',
            'quantity': quantity,
        }

        if bookable.thumbnail:
            item['images'] = [bookable.thumbnail.url]

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=self.request.user.email,
            line_items=[item],
            payment_intent_data={
                'capture_method': 'manual',
            },
            success_url=urljoin(settings.APP_ROOT_URL, reverse('users_profile')),
            cancel_url=urljoin(settings.APP_ROOT_URL, reverse('service_booking', kwargs={'slug': slug}))
        )

        BookedService.objects.create(
            user=self.request.user,
            name=bookable.name,
            summary=summary,
            total_price=bookable.price * quantity,
            stripe_session_id=session.id,
            quantity=quantity
        )

        return HttpResponseRedirect(reverse('service_booking_overview')+f"?session_id={session.id}")

    def form_invalid(self, form):
        print(form.errors)
        messages.error(self.request, "There was an error. Please try again, or contact the admin.")
        return super().form_invalid(form)


class ServiceBookingOverviewView(LoginRequiredMixin, TemplateView):
    template_name = "service_booking_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.request.GET.get('session_id')
        try:
            booked_service = BookedService.objects.get(stripe_session_id=session_id)
        except BookedService.DoesNotExist:
            raise ValidationError('Bad request')
        context["booked_service"] = booked_service
        return context


class ServiceBookStripeRedirect(LoginRequiredMixin, TemplateView):
    template_name = "service_booking_stripe.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["STRIPE_PUBLISHABLE_KEY"] = settings.STRIPE_PUBLISHABLE_KEY
        return context


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    if not "HTTP_STRIPE_SIGNATURE" in request.META:
        return HttpResponse(status=400)
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_SIGNING_SECRET
        )
    except ValueError:
        # Invalid payload
        print("invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        print("invalid signature")
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        try:
            booked_service = BookedService.objects.get(stripe_session_id=session['id'])
        except BookedService.DoesNotExist:
            return HttpResponse(status=400)
        booked_service.payment_status = BookedService.STATUS_COMPLETED
        booked_service.save()

        mail_body = "Name: {0}\nTotal price: {1}\nSummary:\n{2}".format(
            booked_service.name,
            booked_service.total_price,
            booked_service.summary
        )

        send_mail(
            'ASST - Service booked!',
            "We're glad to inform you that the following service has been booked: \n" +
            mail_body,
            settings.DEFAULT_FROM_EMAIL,
            [booked_service.user.email],
            fail_silently=False
        )

        send_mail(
            'ASST - Service booked!',
            "The following service has been booked by {0} : \n".format(booked_service.user.email) +
            mail_body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False
        )

    return HttpResponse(status=200)
