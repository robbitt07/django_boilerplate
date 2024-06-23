"""
Extend createsuperuser command to allow non-interactive creation of a
superuser.

Example usage:

    manage.py create_admin \
                --primary_email foo@foo.foo \
                --password foo \
                --phone 123-456-9900
"""
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError


class Command(createsuperuser.Command):
    help = "Create a superuser with a password non-interactively"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--password", dest="password", default=None,
            help="Specifies the password for the superuser.",
        )
        parser.add_argument(
            "--phone", dest="phone", default=None,
            help="Specifies the phone for the superuser.",
        )
        parser.add_argument(
            "--primary_email", dest="email", default=None,
            help="Specifies the email for the superuser.",
        )

    def handle(self, *args, **options):
        options.setdefault("interactive", True)
        password = options.get("password")
        phone = options.get("phone")
        email = options.get("email")

        if not password or not phone or not email:
            raise CommandError(
                    "--email --phone and --password are required options")

        user_data = {
            "email": email,
            "password": password,
            "phone": phone
        }

        self.UserModel._default_manager.db_manager().create_superuser(**user_data)

        if options.get("verbosity", 0) >= 1:
            self.stdout.write("Superuser created successfully.")