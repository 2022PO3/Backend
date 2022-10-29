from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework import status
from src.api.serializers.users_serializer import UsersSerializer
from rest_framework.views import APIView
from src.users.models import User


class UserList(APIView):
    """
    A view class to get all the users.
    """

    def get(self, request: Request, format=None) -> Response:
        garages = User.objects.all()
        serializer = UsersSerializer(garages, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
