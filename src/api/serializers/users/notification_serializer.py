from rest_framework import serializers

from src.api.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing GET requests of notifications.
    """

    class Meta:
        model = Notification
        fields = ["id", "seen", "title", "content", "created_at"]


class PutNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing PUT requests of notifications.
    """

    class Meta:
        model = Notification
        fields = ["seen"]
