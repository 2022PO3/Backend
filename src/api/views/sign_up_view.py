from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request

from src.api.serializers.users_serializer import UsersSerializer
from src.users.models import User


class SignUpView(APIView):
    def post(self, request: Request, format=None) -> Response:
        user_data = JSONParser().parse(request)
        user_serializer = UsersSerializer(data=user_data)
        if user_serializer.is_valid():
            User.objects.create_user(
                user_serializer["email"],
                user_serializer["password"],
                user_serializer["role"],
            )
            return Response(
                {"data": user_serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"errors": user_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
