from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny

from src.core.views import BackendResponse
from src.users.models import User
from src.api.serializers import SignUpSerializer


class SignUpView(APIView):
    """
    General sign up view for new users. An `email`, `password` and `role` have to be
    provided to create a user. The `first_name` and `last_name` fields are optional.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, format=None) -> BackendResponse:
        user_data = JSONParser().parse(request)
        user_serializer = SignUpSerializer(data=user_data)
        if user_serializer.is_valid():
            try:
                validated_user_data = user_serializer.validated_data
                User.objects.create_user(
                    validated_user_data["email"],
                    validated_user_data["password"],
                    validated_user_data["role"],
                    first_name=user_serializer.data["firstName"],
                    last_name=user_serializer.data["lastName"],
                )
                return BackendResponse(
                    user_serializer.data, status=status.HTTP_201_CREATED
                )
            except ValidationError as e:
                return BackendResponse(e.error_list, status=status.HTTP_400_BAD_REQUEST)
        return BackendResponse(
            user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
