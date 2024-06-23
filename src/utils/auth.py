from django.conf import settings
from django.contrib.auth.models import update_last_login

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from apps.appadmin.serializers import UserSerializer

from typing import Any, Dict


def jwt_response_handler(token, user=None, request=None):
    return {
        "token": token,
        "user": UserSerializer(user, context={"request": request}).data
    }


class TokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["token"] = str(refresh.access_token)
        data["refresh_token"] = str(refresh)
        data["user"] = UserSerializer(
            self.user, context=self.context
        ).data

        if settings.SIMPLE_JWT.get("UPDATE_LAST_LOGIN", False):
            update_last_login(None, self.user)

        return data
