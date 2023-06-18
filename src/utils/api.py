from django.conf import settings

from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ParseError

from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from apps.customer.config import get_or_set_customer_user_config, Config

import logging
import sys


api_logger = logging.getLogger('api')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UserApiMixin:
    authentication_classes = [
        SessionAuthentication, TokenAuthentication, JSONWebTokenAuthentication
    ]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        qs = super(UserApiMixin, self).get_queryset()
        return qs.filter(customer=self.request.customer)

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)
        # API Processing Additional Permissions per User
        if self.request.user.is_authenticated:
            self.request.customer = self.request.user.customer
            customer_config, user_config = get_or_set_customer_user_config(
                customer_id=self.request.customer.id,
                user_id=self.request.user.id
            )
            self.request.app_config = Config(
                customer_config=customer_config, user_config=user_config
            )

    def handle_invalid_request(self, message, error_code):
        raise ParseError(detail={'message': message, 'code': error_code})

    def handle_not_found_request(self, message, error_code):
        raise NotFound(detail={'message': message, 'code': error_code})

    def handle_logging_info(self, msg):
        api_logger.info(msg=msg)

    def handle_warning(self, msg):
        api_logger.warning(msg=msg)
        return

    def handle_exception(self, exc, msg=None):
        if msg is not None:
            msg = msg
        elif isinstance(exc, (exceptions.NotAuthenticated,
                              exceptions.AuthenticationFailed)):
            msg = "Authentication warning or error"
        else:
            msg = "Error with API call"
        api_logger.warning(
            msg=msg, exc_info=True
        )

        return super().handle_exception(exc)

    def raise_uncaught_exception(self, exc):
        api_logger.error(
            msg=f"Uncaught API serverside error",
            exc_info=exc,
            extra={}
        )
        super().raise_uncaught_exception(exc)

    def perform_create(self, serializer, **kwargs):
        serializer.save(
            customer=self.request.customer, updated_by=self.request.user, **kwargs
        )

    def perform_update(self, serializer, **kwargs):
        serializer.save(updated_by=self.request.user, **kwargs)