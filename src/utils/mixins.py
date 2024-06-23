from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.generic.base import ContextMixin

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.models import TokenUser

from apps.appadmin.options import DEFAULT_USER_PREFERENCES


from functools import lru_cache
from logging import getLogger

User = get_user_model()


@lru_cache
def get_user_cache(id: int) -> User:
	return User.objects.get(pk=id)


api_logger = getLogger("api")


class AdminMixin(UserPassesTestMixin, ContextMixin):
	"""Admin Mixin for Admin Views"""

	def test_func(self):
		return self.request.user.is_admin


class CustomerPermissionsViewMixin(UserPassesTestMixin):
    """ Place holder mixin for Permission"""

    def test_func(self):
        return self.request.user.customer_id is not None


class CustomerViewMixin(CustomerPermissionsViewMixin):

    def get_queryset(self, *args, **kwargs):
        qs = super(CustomerViewMixin, self).get_queryset()
        return qs.filter(customer=self.request.customer)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["context"] = {"customer": getattr(
            self.request, "customer", None)}
        return kwargs

    def clean_form(self, form):
        form.instance.updated_by = self.request.user
        return form

    def form_valid(self, form):
        # Updated Created/Updated by
        form = self.clean_form(form)
        self.object = form.save(commit=False)

        self.object.customer = self.request.customer
        try:
            self.object.save()
        except IntegrityError:
            # TODO: Add Logging here
            form.add_error(None, ValidationError("Error saving record"))
            return self.form_invalid(form)
        return super(CustomerViewMixin, self).form_valid(form)

    def save_model(self, request, obj, form, change):
        customer = self.request.customer
        if obj.customer is None:
            obj.customer = customer
        else:
            if obj.customer != customer:
                raise Exception("Cross customer exception error")
        super().save_model(request, obj, form, change)


class ApiMixin:

	def initial(self, request, *args, **kwargs):
		"""
		Runs anything that needs to occur prior to calling the method handler.

		Added to initial DRF method, including Customer, Customer Config, App Config
		and likely more items to come. Needs to mirror the `.middleware.UserCustomerMiddleware`
		"""
		super().initial(request, *args, **kwargs)
		# API Processing Additional Permissions per User/Customer
		if self.request.user.is_authenticated:

			# Get Database side User Model
			if isinstance(self.request.user, TokenUser):
				self.request.token_user = self.request.user
				self.request.user = get_user_cache(id=self.request.user.pk)

			self.request.user_preferences = cache.get(
				f"user_preferences:{request.user.pk}", DEFAULT_USER_PREFERENCES
			)

	def perform_create(self, serializer, **kwargs):
		serializer.save(
			created_by=self.request.user, updated_by=self.request.user,
			**kwargs
		)

	def perform_update(self, serializer, **kwargs):
		serializer.save(updated_by=self.request.user, **kwargs)


class CommonAPIPermMixin(ApiMixin):
	authentication_classes = [
		SessionAuthentication, TokenAuthentication, JWTStatelessUserAuthentication
	]
	permission_classes = [IsAuthenticated]
