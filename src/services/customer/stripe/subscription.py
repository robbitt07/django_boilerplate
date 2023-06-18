from django.conf import settings

from apps.customer.models import Subscription

import logging
import stripe

logger = logging.getLogger('service')

STRIPE_SUBSCRIPTIONS = [
    {'code': "monthly_premium_<django_package_name>"},
    {'code': "monthly_pro_<django_package_name>"}
]


def sync_subscription(code):
    stripe.api_key = settings.STRIPE_SECRET_API_KEY
    stripe_prices = stripe.Price.list(lookup_keys=[code]).data
    if len(stripe_prices) > 0:
        if len(stripe_prices) > 1:
            logger.warn(f"Multiple Strip Price Codes `{code}` exists", extra={'task': 'SyncStripeSubscription'})
            stripe_prices = stripe_prices[:1]
        
        # Get Price data
        price_data = stripe_prices[0]
        
        # Get Product
        product_data = stripe.Product.retrieve(price_data.product)
        
        # Get or Create Product
        subscription_obj, created = Subscription.objects.get_or_create(
            code=code,
            integration='STRIPE',
            defaults={'name': product_data.name, 'description': product_data.description},
        )
        if created:
            logger.info(
                f"Created Subscription for code=`{code}` with id=`{subscription_obj.pk}`", 
                extra={'task': 'SyncStripeSubscription'}
            )
        else:
            logger.info(
                f"Updated Subscription for code=`{code}` with id=`{subscription_obj.pk}`", 
                extra={'task': 'SyncStripeSubscription'}
            )
        # Update Info
        subscription_obj.name = product_data.name
        subscription_obj.description = product_data.description
        subscription_obj.active = product_data.active
        # Update Meta (aka reference key)
        subscription_obj.meta = {
            'stripe_price_id': price_data.id
        }
        subscription_obj.save()

    else:
        logger.Error(
            f"Strip Price Code `{code}` is missing", extra={'task': 'SyncStripeSubscription'}
        )
