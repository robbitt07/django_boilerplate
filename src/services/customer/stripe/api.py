from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.utils import timezone

from rest_framework import status

from apps.customer.models import Customer, CustomerSubscription

from datetime import datetime
import logging
import stripe

logger = logging.getLogger("integration")


class StripeWebhook(View):
    
    def post(self, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_API_KEY
        payload = self.request.body
        sig_header = self.request.META["HTTP_STRIPE_SIGNATURE"]
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_API_KEY
            )
        except ValueError as e:
            logger.info("Error with Strip Webhook", exc_info=True)
            # Invalid payload
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            logger.info("Error with Strip Webhook", exc_info=True)
            # Invalid signature
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        if event.type == "payment_intent.succeeded":
            logger.info(f"PaymentIntent was successful!", extra={"payload": event})
        elif event.type == "customer.subscription.deleted":
            logger.info(f"Stripe Subscription `{event.data.object.id}` deleted", extra={"payload": event})
            # Deactive Subscription Now (Internally Deleted)
            try:
                customer_subscription_obj = CustomerSubscription.objects.get(meta__subscription_id=event.data.object.id)
                customer_subscription_obj.deactive_date = timezone.now()
                customer_subscription_obj.save()
            except CustomerSubscription.DoesNotExist:
                logger.error(
                    f"Stripe Subscription `{event.data.object.id}` failed to be deleted as unable to find matching internal CustomerSubscription record", 
                    exc_info=True
                )
                return HttpResponse(status=404)
        elif event.type == "customer.subscription.updated":
            try:
                customer_subscription_obj = CustomerSubscription.objects.get(meta__subscription_id=event.data.object.id)
            except CustomerSubscription.DoesNotExist:
                logger.error(
                    f"Stripe Subscription `{event.data.object.id}` failed to be updated as unable to find matching internal CustomerSubscription record", 
                    exc_info=True,
                    extra={"payload": event}
                )
                return HttpResponse(status=404)
            # Cancelled Subscription
            if event.data.object.cancel_at_period_end:
                logger.info(f"Stripe Subscription `{event.data.object.id}` cancelled", extra={"payload": event})
                # Make Cancel At Period End TZ Aware
                deactive_date = timezone.make_aware(
                    datetime.fromtimestamp(event.data.object.current_period_end), timezone.get_current_timezone()
                )
                customer_subscription_obj.deactive_date = deactive_date
                customer_subscription_obj.save()
            
            elif not event.data.object.cancel_at_period_end and event.data.previous_attributes.cancel_at_period_end:
                logger.info(f"Stripe Subscription `{event.data.object.id}` renewed", extra={"payload": event})
                # Renew Subscription
                customer_subscription_obj.deactive_date = None
                customer_subscription_obj.save()
            else:
                logger.info(f"Unknown Stripe Subscription update: `{event.data.object.id}`", extra={"payload": event})
        elif event.type == "setup_intent.setup_failed":
            logger.info("Setup Failed\n", event.data.object, extra={"payload": event})
        elif event.type == "setup_intent.succeeded":
            # Update Customer to Have Integration Payment Active
            try:
                customer_obj = Customer.objects.get(integration_key=event.data.object.customer)
            except Customer.DoesNotExist:
                logger.error(
                    f"Stripe Setup `{event.data.object.customer}` failed as unable to find matching internal Customer record", 
                    exc_info=True,
                    extra={"payload": event}
                )
                return HttpResponse(status=404)
            customer_obj.integration_payment_active = True
            customer_obj.save()
            # Get Active Subscription
            active_subscription = customer_obj._active_subscription
            if active_subscription is not None:
                active_subscription.payment_active_date = timezone.make_aware(
                    datetime.fromtimestamp(event.created), timezone.get_current_timezone()
                )
                active_subscription.save()
            logger.info("Setup Succeeded", extra={"payload": event})
        else:
            logger.info("Unhandled event type {}".format(event.type), extra={"payload": event})

        return HttpResponse(status=200)