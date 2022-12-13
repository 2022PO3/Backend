from base64 import urlsafe_b64decode
from django.utils.encoding import force_str
from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.serializers import UserSerializer, ChangePasswordSerializer
from src.core.views import (
    PkAPIView,
    _OriginAPIView,
    BackendResponse,
    parse_frontend_json,
)
from src.core.exceptions import BackendException
from src.users.models import User
from src.users.backends import EmailVerificationTokenGenerator


class UserDetailView(PkAPIView):
    """
    A view class to get or update the information about the currently logged user.
    """

    origins = ["app", "web"]

    serializer = UserSerializer


class UserActivationView(_OriginAPIView):
    """
    A view class to handle incoming requests for user activation.
    """

    permission_classes = [AllowAny]
    origins = ["web", "app"]

    def get(self, request: Request, uid_b64: str, token: str) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            user = UserActivationView._get_user_from_email_verification_token(
                str(uid_b64), str(token)  # str() to prevent type injection attacks
            )
        except BackendException as e:
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        return BackendResponse(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _get_user_from_email_verification_token(uid_b64: str, token: str) -> User:
        try:
            uid = force_str(urlsafe_b64decode(uid_b64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise BackendException("The user could not be found.")
        if user is not None and EmailVerificationTokenGenerator().check_token(
            user, token
        ):
            return user
        raise BackendException("Validation of the activation token failed.")


class ChangePasswordView(_OriginAPIView):
    origins = ["app", "web"]

    def put(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().put(request, format)) is not None:
            return resp
        data = parse_frontend_json(request)
        serializer = ChangePasswordSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            user = request.user
            if not check_password(
                serializer.validated_data["old_password"], user.password  # type: ignore
            ):
                return BackendResponse(
                    ["The entered password is incorrect"],
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user.set_password(serializer.validated_data["new_password"])  # type: ignore
            user.save()
            return BackendResponse(None, status=status.HTTP_204_NO_CONTENT)
        return BackendResponse([serializer.errors], status=status.HTTP_400_BAD_REQUEST)  # type: ignore
