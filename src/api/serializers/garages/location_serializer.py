from rest_framework import serializers

from src.api.models import Location


class LocationsSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing requests of locations.
    """

    class Meta:
        model = Location
        fields = [
            "id",
            "country",
            "province",
            "municipality",
            "post_code",
            "street",
            "number",
        ]
