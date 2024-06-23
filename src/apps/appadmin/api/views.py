from django.core.cache import cache

from rest_framework import serializers
from rest_framework.generics import GenericAPIView

from utils.mixins import CommonAPIPermMixin
from utils.yahp.cache import MONTH
from utils.yahp.api import api_response_wrapper


class UserPreferencesSerializer(serializers.Serializer):
	"""
	User Preferences serializer, add UI and other user preferences that is passed
	to the request with request.user_preferences.
	"""
	sidebar_mini = serializers.BooleanField(required=False)


class UserPreferencesView(CommonAPIPermMixin, GenericAPIView):
    """
    Get or Set User Preferences
    """
    serializer_class = UserPreferencesSerializer

    def get(self, *args, **kwargs):
        user_id = self.request.user.pk
        user_preferences = cache.get(f"user_preferences:{user_id}", {})
        return api_response_wrapper(payload=user_preferences, status=200)

    def post(self, *args, **kwargs):
        user_id = self.request.user.pk
        user_preferences = cache.get(f"user_preferences:{user_id}", {})
        s = self.get_serializer(data=self.request.data)
        if s.is_valid():
            for key, value in s.validated_data.items():
                user_preferences.update({key: value})

            cache.set(
                f"user_preferences:{user_id}", user_preferences, MONTH
            )
            return api_response_wrapper(payload=user_preferences, status=201)

        return api_response_wrapper(
            payload=None, status=404, warnings=s.errors
        )
