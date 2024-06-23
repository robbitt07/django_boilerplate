from django.urls import path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.appadmin.api.views import UserPreferencesView


urlpatterns = [
    path("api/v1/token-auth/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/user-preferences/", UserPreferencesView.as_view(), name="user_preferences"),

    # OpenAPI 3 documentation with Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            template_name="swagger-ui.html", url_name="schema"
        ),
        name="swagger-ui",
    ),
]
