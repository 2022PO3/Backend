from django.utils import timezone

from knox.models import AuthToken
from knox.settings import knox_settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from src.api.serializers.users_serializer import LoginSerializer, UsersSerializer
from src.users.models import User


class LoginView(APIView):
    def get_token_limit_per_user(self):
        return knox_settings.TOKEN_LIMIT_PER_USER

    def post(self, request: Request, format=None) -> Response:
        login_data = JSONParser().parse(request)
        login_serializer = LoginSerializer(data=login_data)
        if login_serializer.is_valid():
            token_limit_per_user = self.get_token_limit_per_user()
            user = User.objects.get(email=login_serializer.validated_data)

            if token_limit_per_user is not None:
                now = timezone.now()
                token = user.auth_token_set.filter(expiry__gt=now)
                if token.count() >= token_limit_per_user:
                    return Response(
                        {
                            "errors": [
                                "Maximum amount of tokens allowed per user exceeded."
                            ]
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            return Response(
                {
                    "data": {
                        "user": UsersSerializer(user).data,
                        "token": AuthToken.objects.create(user)[1],
                    }
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": ["Invalid credentials entered."]},
            status=status.HTTP_401_UNAUTHORIZED,
        )
