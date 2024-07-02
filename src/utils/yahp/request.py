from django.contrib.auth import get_user_model

User = get_user_model()


class AbstractRequest(object):

    def __init__(self, user: User) -> None:
        self._user = user

    @property
    def user(self):
        return self._user

    def __str__(self) -> str:
        return str(self.user)
