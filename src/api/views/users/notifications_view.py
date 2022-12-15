from src.api.models import Notification
from src.api.serializers import NotificationSerializer, PutNotificationSerializer

from src.core.views import BaseAPIView, PkAPIView
from src.users.permissions import IsUserNotification


class NotificationsView(BaseAPIView):
    """
    A view class to get all notification from the currently logged in user.
    """

    origins = ["app", "web"]
    serializer = {"get": NotificationSerializer}
    model = Notification
    get_user_id = True


class PkNotificationsView(PkAPIView):
    """
    A view class to delete a given notification from the currently logged in user or to set it to 'seen'.
    """

    origins = ["app", "web"]
    permission_classes = [IsUserNotification]
    serializer = PutNotificationSerializer
    model = Notification
    user_id = True
