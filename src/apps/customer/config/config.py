"""
Customer Config including User Permissions, Customer Configuration (Subscription etc),
and Desired Config items
"""
from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.customer.models import Customer

from typing import Dict, Tuple

User = get_user_model()


def get_or_set_customer_user_config(customer_id: str, user_id: str) -> Tuple[Dict, Dict]:    
    """
    Cache to Get or Set User and Customer Config

    Parameters
    -----------
        customer_id int
            Customer ID
        user_id int
            User ID
    Returns
    -----------
        customer_config dict
            Customer Config object
        user_config dict
            User Config Object
    """
    # Get Customer Config
    customer_cache_key = f"customer_config:{customer_id}"
    customer_config = cache.get(customer_cache_key, None)
    if customer_config is None:
        customer_obj = Customer.objects.get(pk=customer_id)
        customer_config = {
            "trial": customer_obj.trail_account,
            "active": customer_obj.integration_payment_active and customer_obj.has_active_subscription,
            "integration_key": customer_obj.get_or_create_integration_key()
        }
        ## Set Customer Config
        cache.set(customer_cache_key, customer_config, 86400)

    # Get User Config
    user_cache_key = f"user_config:{user_id}"
    user_config = cache.get(user_cache_key, None)
    if user_config is None:
        user_obj = User.objects.get(pk=user_id)
        user_config = {
            "customer_staff": user_obj.customer_staff,
            "customer_admin": user_obj.customer_admin,
        }
        ## Set Customer Config
        cache.set(user_cache_key, user_config, 86400)

    return customer_config, user_config


class Config(object):
    def __init__(self, customer_config, user_config):
        self._customer_config = customer_config
        self._user_config = user_config
        self._set_customer_config()
        self._set_user_config()

    def _set_customer_config(self):
        for key, value in self._customer_config.items():
            setattr(self, f"customer_{key}", value)

    def _set_user_config(self):
        for key, value in self._user_config.items():
            setattr(self, f"user_{key}", value)

    