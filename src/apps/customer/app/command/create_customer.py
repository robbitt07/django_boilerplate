from apps.customer.models import Customer

from hashlib import sha1


def create_customer(name: str,
                    customer_primary_email: str,
                    trail_account: bool = True) -> Customer:
    # Validate Name (Max 100 characters)
    if len(str(name)) > 100:
        raise ValueError("Customer Name must be less than 100 characters")

    # Generate Name Hash
    name_hash = f"cust_{sha1(str(name).encode("utf-8")).hexdigest()[0:14]}"

    # Create Customer
    # TODO: Additional Steps?
    return Customer.objects.create(
        name=name,
        name_hash=name_hash,
        customer_primary_email=customer_primary_email,
        trail_account=trail_account
    )
