from django.utils import timezone

from knox.models import AuthToken
from knox.settings import knox_settings

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny

from src.api.serializers import LoginSerializer, UserSerializer
from src.core.views import BackendResponse, _OriginAPIView
from src.users.models import User


class LoginView(_OriginAPIView):
    """
    A view to log in a user.
    """

    permission_classes = [AllowAny]
    origins = ["web", "app"]
    http_method_names = ["post"]

    def get_token_limit_per_user(self):
        return knox_settings.TOKEN_LIMIT_PER_USER

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        login_data = JSONParser().parse(request)
        login_serializer = LoginSerializer(data=login_data)
        if login_serializer.is_valid():
            token_limit_per_user = self.get_token_limit_per_user()
            user: User = User.objects.get(email=login_serializer.validated_data)

            if token_limit_per_user is not None:
                now = timezone.now()
                token = user.auth_token_set.filter(expiry__gt=now)  # type: ignore
                if token.count() >= token_limit_per_user:
                    return BackendResponse(
                        ["Maximum amount of tokens allowed per user exceeded."],
                        status=status.HTTP_403_FORBIDDEN,
                    )

            return BackendResponse(
                {
                    "user": UserSerializer(user).data,
                    "token": AuthToken.objects.create(user)[1],
                },
                status=status.HTTP_200_OK,
            )

        return BackendResponse(
            ["Invalid credentials entered."],
            status=status.HTTP_401_UNAUTHORIZED,
        )
