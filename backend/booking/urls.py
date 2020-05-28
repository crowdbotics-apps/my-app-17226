from django.urls import path

from .views import (ServiceBookingOverviewView, ServiceBookingView,
                    ServiceBookStripeRedirect, ServiceListView,
                    stripe_webhook_view, PublicServiceListView)
from .views_admin import (AdminBookedServiceListView, BookableCreateView,
                          BookableDeleteView, BookableList,
                          BookedServiceAssignWorker, WorkerCreateView,
                          WorkerDeleteView, WorkerListView, BookableUpdateView,
                          BookableInputListView, BookableInputCreateView, BookableInputDeleteView)
from .views_worker import WorkerDashboardView

urlpatterns = [
    path('service-list/', PublicServiceListView.as_view(), name="public_service_list"),

    path('manage/bookable/update/<slug:slug>/', BookableUpdateView.as_view(), name="manage_bookable_update"),
    path('manage/bookable/create/', BookableCreateView.as_view(), name="manage_bookable_create"),
    path('manage/bookable/', BookableList.as_view(), name="manage_bookable_list"),
    path('manage/bookable/delete/<slug:slug>/', BookableDeleteView.as_view(), name="manage_bookable_delete"),

    path('manage/bookable/inputs/<slug:slug>/', BookableInputListView.as_view(), name="manage_bookable_input_list"),
    path('manage/bookable/inputs/<slug:slug>/create/', BookableInputCreateView.as_view(), name="manage_bookable_input_create"),
    path('manage/bookable/inputs/<slug:slug>/delete/<int:pk>/', BookableInputDeleteView.as_view(), name="manage_bookable_input_delete"),

    path('manage/booked-services/', AdminBookedServiceListView.as_view(), name="manage_booked_services"),
    path('manage/booked-services/<int:pk>/assign/', BookedServiceAssignWorker.as_view(), name="manage_booked_services_assign"),

    path('manage/workers/', WorkerListView.as_view(), name="manage_worker_list"),
    path('manage/workers/create/', WorkerCreateView.as_view(), name="manage_worker_create"),
    path('manage/workers/delete/', WorkerDeleteView.as_view(), name="manage_worker_delete"),

    path('worker-dashboard/', WorkerDashboardView.as_view(), name="worker_dashboard"),

    path('payments/', ServiceBookStripeRedirect.as_view(), name="service_booking_stripe"),
    path('payments/webhook/', stripe_webhook_view, name="stripe_webhook"),

    path('services/<slug:slug>/', ServiceBookingView.as_view(), name="service_booking"),
    path('payments/booking-overview/', ServiceBookingOverviewView.as_view(), name="service_booking_overview"),

    
    path('', ServiceListView.as_view(), name="service_list"),
]
