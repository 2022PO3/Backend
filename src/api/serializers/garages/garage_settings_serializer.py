from typing import Any

from src.api.models import GarageSettings, Location
from src.api.serializers import LocationsSerializer
from src.core.serializers import APIForeignKeySerializer


class GarageSettingsSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing GET- and POST-requests of the garage settings.
    """

    location = LocationsSerializer()

    class Meta:
        model = GarageSettings
        fields = [
            "id",
            "location",
            "electric_cars",
            "max_height",
            "max_width",
            "max_handicapped_lots",
        ]

    def create(self, validated_data: dict[str, Any]) -> GarageSettings:
        """
        Override of the default `create()`-method, for allowing  the post of nested
        JSON-objects. First, a `Locations`-object is created, whereafter a
        `GarageSettings`-object is created with the `Locations`-object created earlier.
        """
        locationData = validated_data.pop("location")
        location = Location.objects.create(**locationData)
        return GarageSettings.objects.create(location=location, **validated_data)

    def update(self, validated_data: dict[str, Any]) -> GarageSettings:
        """
        Override of the default `update()`-method, for allowing  the post of nested
        JSON-objects. First, a `Locations`-object is created, whereafter a
        `GarageSettings`-object is created with the `Locations`-object created earlier.
        """
        locationData = validated_data.pop("location")
        location = Location.objects.create(**locationData)
        return GarageSettings.objects.create(location=location, **validated_data)
