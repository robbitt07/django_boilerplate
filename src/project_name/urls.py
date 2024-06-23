from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from apps.appadmin import views as admin_views
from .api_urls import urlpatterns as api_urlpatterns


urlpatterns = [
    # TemplateView -- input favico
    path("admin/", admin.site.urls),
    path("login/", admin_views.LoginUser.as_view(), name="login_user"),
    path("logout/", admin_views.LogoutUser.as_view(), name="logout_user"),
    path("generic-template/", admin_views.GenericTemplateView.as_view(), name="generic_template"),

    # Locations
    path("", admin_views.LandingView.as_view(), name="landing"),
]

urlpatterns += api_urlpatterns

if not settings.USE_REMOTE_FILE_SYSTEM:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)