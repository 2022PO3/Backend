from rest_framework.request import Request

from rest_framework import status

from src.core.views import BackendResponse
from src.core.utils import OriginAPIView
from src.api.serializers import UsersSerializer


class UserDetailView(OriginAPIView):
    """
    A view class to get a user based on its `pk`.
    """

    origins = ["app", "web"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        serializer = UsersSerializer(request.user)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
