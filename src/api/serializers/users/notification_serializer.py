from rest_framework import serializers

from src.api.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing requests of locations.
    """

    class Meta:
        model = Notification
        fields = ["id", "seen", "title", "content"]
