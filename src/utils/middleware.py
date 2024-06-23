from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from apps.customer.config import get_or_set_customer_user_config, Config

from re import compile

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip("/"))]

if hasattr(settings, "LOGIN_EXEMPT_URLS"):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, "user"), "The Login Required middleware\
             requires authentication middleware to be installed. Edit your\
             MIDDLEWARE_CLASSES setting to insert\
             'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
             work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
             'django.core.context_processors.auth'."
        if not request.user.is_authenticated:
            try:
                path = request.path_info.lstrip("/")
                if not any(m.match(path) for m in EXEMPT_URLS) and path != "":
                    return HttpResponseRedirect(settings.LOGIN_URL)
            except:
                return HttpResponseRedirect(settings.LOGIN_URL)


class UserCustomerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if not request.user.is_admin:
                request.customer = request.user.customer
                customer_config, user_config = get_or_set_customer_user_config(
                    customer_id=request.customer.id,
                    user_id=request.user.id
                )
                request.app_config = Config(
                    customer_config=customer_config, user_config=user_config
                )
