from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password

from rest_framework.request import Request

from src.users.models import User


class EmailAuthBackend(BaseBackend):
    """
    Authenticate a user with a email/password pair.
    """

    def authenticate(self, request: Request, email: str, password: str) -> User | None:
        """
        Authenticate a user based and password.
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id: int) -> User | None:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
