from django.urls import path
from .views import ProfileDetailView, ProfileUpdateView


urlpatterns = [
    path('profile/', ProfileDetailView.as_view(), name="users_profile"),
    path('profile/update/', ProfileUpdateView.as_view(), name="users_profile_update"),
]
