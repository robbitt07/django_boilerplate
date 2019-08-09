from django.urls import path, include

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('api/v1/token-auth/', obtain_jwt_token),

]