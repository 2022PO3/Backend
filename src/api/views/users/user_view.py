from src.core.views import BaseAPIView
from src.api.serializers import UsersSerializer


class UserDetailView(BaseAPIView):
    """
    A view class to get to get the information about the currently logged user.
    """

    origins = ["app", "web"]

    serializer = UsersSerializer
