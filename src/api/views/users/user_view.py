from rest_framework.request import Request

from rest_framework import status
from rest_framework.parsers import JSONParser

from src.core.views import BackendResponse
from src.core.utils import OriginAPIView
from src.api.serializers import GetUsersSerializer


class UserDetailView(OriginAPIView):
    """
    A view class to get a user based on its `pk`.
    """

    origins = ["app", "web"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        serializer = GetUsersSerializer(request.user)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().put(request, format)) is not None:
            return resp
        request_user_data = JSONParser().parse(request)
        user_serializer = GetUsersSerializer(request.user, data=request_user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return BackendResponse(user_serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
