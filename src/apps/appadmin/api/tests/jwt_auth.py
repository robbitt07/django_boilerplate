from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication

from django_seed import Seed

seeder = Seed.seeder()
User = get_user_model()

class TestAccessTokenValidation(APITestCase):

    def test_should_raise_error_if_no_authorization_header_is_available(self):

        # Add dummy data to the Facility and Trading Table
        seeder.add_entity(User, 1)
        # seeder.add_entity(Facility, 5)
        seeder.execute()

        # we expect the result in 1 query
        response = self.client.get(reverse("trading_partner-list"), format="json")

        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertAlmostEqual(response.json()["detail"], "Authentication credentials were not provided.")
