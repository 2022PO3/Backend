from rest_framework.request import Request

from rest_framework import status
from rest_framework.views import APIView

from src.core.views import BackendResponse
from src.api.serializers import UsersSerializer


class UserDetail(APIView):
    """
    A view class to get a user based on its `pk`.
    """

    def get(self, request: Request, format=None) -> BackendResponse:
        serializer = UsersSerializer(request.user)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
