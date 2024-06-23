from django.views.generic import ListView

from apps.customer.models import Customer
from utils.mixins import AdminMixin


class AdminLanding(AdminMixin, ListView):
    model = Customer
    template_name = "customer/admin/landing.html"