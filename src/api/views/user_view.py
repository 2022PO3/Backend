from django.http import Http404

from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework import status, permissions
from rest_framework.views import APIView

from src.core.views import GetObjectMixin
from src.users.models import User
from src.api.serializers import UsersSerializer


class UserDetail(GetObjectMixin, APIView):
    """
    A view class to get a user based on its `pk`.
    """

    def get(self, request: Request, format=None) -> Response:
        serializer = UsersSerializer(request.user)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
