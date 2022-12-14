from rest_framework import serializers

from src.api.models import Notification


class LocationsSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing requests of locations.
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "country",
            "province",
            "municipality",
            "post_code",
            "street",
            "number",
        ]
