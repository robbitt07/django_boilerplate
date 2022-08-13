from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.generic.base import ContextMixin

import logging

api_logger = logging.getLogger('api')


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
        kwargs['context'] = {'customer': getattr(self.request, 'customer', None)}
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
                raise Exception('Cross customer exception error')
        super().save_model(request, obj, form, change)