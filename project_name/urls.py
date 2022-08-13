from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from apps.appadmin import views as admin_views
from .api_urls import urlpatterns as api_urlpatterns

urlpatterns = [
    # TemplateView -- input favico
    path('admin/', admin.site.urls),
    path('login/', admin_views.login_user, name='login_user'),
    path('logout/', admin_views.logout_user, name='logout'),
]

urlpatterns += api_urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)