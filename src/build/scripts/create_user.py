### --- Django Config ----
import django
import os
import sys

sys.path.append(os.curdir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yabpt.settings.development")
django.setup()

# --- Create User --------------------------------------------------------------
# TODO: Add Customer, Subscription, Configuration
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.appadmin.options import *

from decouple import Config, RepositoryEnv

import test_variables
config = Config(RepositoryEnv(".env"))

# Create User
User = get_user_model()

user_obj = User.objects.create_superuser(
    email=test_variables.ADMIN_EMAIL,
    password=config("TEST_USER_PW", cast=str),
    first_name="Test",
    last_name="User"
)