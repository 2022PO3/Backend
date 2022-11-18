from rest_framework import serializers

from src.api.models import Locations
from src.api.models import ProvincesEnum


class LocationsSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing both GET and POST-requests of locations.
    """

    postCode = serializers.IntegerField(source="post_code")

    class Meta:
        model = Locations
        fields = [
            "id",
            "country",
            "province",
            "municipality",
            "postCode",
            "street",
            "number",
        ]
