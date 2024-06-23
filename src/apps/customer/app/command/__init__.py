from collections import namedtuple

from .create_customer import create_customer

Command = namedtuple("Command", [
    "create_customer"
])


command = Command(
    create_customer=create_customer
)
