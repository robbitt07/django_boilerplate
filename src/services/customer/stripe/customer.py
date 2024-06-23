from django.conf import settings

import stripe


def stripe_create_customer(id: int, name:str , customer_primary_email:str) -> str:
    stripe.api_key = settings.STRIPE_SECRET_API_KEY
    res = stripe.Customer.create(
        name=name,
        email=customer_primary_email,
        metadata={"source_id": id}
    )
    # TODO: Error Handling and Logging
    return res.id