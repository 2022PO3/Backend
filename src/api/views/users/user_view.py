from src.core.views import PkAPIView
from src.api.serializers import UsersSerializer


class UserDetailView(PkAPIView):
    """
    A view class to get or update the information about the currently logged user.
    """

    origins = ["app", "web"]

    serializer = UsersSerializer
