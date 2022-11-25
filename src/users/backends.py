from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.backends import BaseBackend

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


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def make_token(self, user: User) -> str:
        """
        Create a token that can be used once to active a user's account.
        """
        return super().make_token(user)

    def _make_hash_value(self, user: User, timestamp) -> str:
        """
        Creates a hash of the user's active state, primary key and the timestamp of token 
        creation.
        """
        return str(user.is_active) + str(user.pk) + str(timestamp)


email_verification_token = EmailVerificationTokenGenerator()
