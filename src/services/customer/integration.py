from .stripe import stripe_create_customer


class CustomerIntegration(object):
    def __init__(self, customer_obj: object):
        self.customer_obj = customer_obj

    def create_customer(self) -> str:
        if self.customer_obj.integration == "STRIPE":
            self.customer_obj.integration_key = stripe_create_customer(
                id=self.customer_obj.pk,
                name=self.customer_obj.name,
                customer_primary_email=self.customer_obj.customer_primary_email
            )
            self.customer_obj.save()
            return self.customer_obj.integration_key
        else:
            raise NotImplementedError(f"Customer Integration `{self.self.customer_obj.integration}` not implemented")