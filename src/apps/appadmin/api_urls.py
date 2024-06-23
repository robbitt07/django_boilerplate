from django.urls import path
from .api import CurrentUser

urlpatterns = [
    path("current_user/", CurrentUser.as_view(), name="current_user"),
]
