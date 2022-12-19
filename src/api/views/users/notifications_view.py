from src.api.models import Notification
from src.api.serializers import NotificationSerializer, PutNotificationSerializer

from src.core.views import BaseAPIView, PkAPIView
from src.users.permissions import IsUserNotification


class NotificationsDetailView(PkAPIView):
    """
    A view class which handles PUT- and DELETE-requests for a notification with `pk`.
    """

    origins = ["app", "web"]
    permission_classes = [IsUserNotification]
    serializer = PutNotificationSerializer
    model = Notification
    user_id = True


class NotificationsListView(BaseAPIView):
    """
    A view class which handles GET-requests for the user's notifications.
    """

    origins = ["app", "web"]
    serializer = {"get": NotificationSerializer}
    model = Notification
    get_user_id = True
