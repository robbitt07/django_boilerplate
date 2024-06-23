from django.urls import path, re_path

from .views import (
    UserDashboardLanding,
    UserActivateView,
    UserAPIView,

    # Admin Side
    AdminLanding
)

app_name = "customer"

urlpatterns = [
    # User Landing
    path("", UserDashboardLanding.as_view(), name="dashboard"),
    path("api-token/", UserAPIView.as_view(), name="api_token"),

    # Admin 
    path("admin/landing/", AdminLanding.as_view(), name="admin_landing"),

    # User Activation
    re_path(
        r"^user-activate/(?P<uidb>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        UserActivateView.as_view(), name="user_activate"
    ),
]
