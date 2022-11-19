from typing import Any

from rest_framework import serializers

from src.api.models import GarageSettings, Locations
from src.api.serializers import LocationsSerializer


class GarageSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing GET- and POST-requests of the garage settings.
    """

    location = LocationsSerializer()
    maxHeight = serializers.FloatField(source="max_height")
    maxWidth = serializers.FloatField(source="max_width")
    maxHandicappedLots = serializers.IntegerField(source="max_handicapped_lots")

    def create(self, validated_data: dict[str, Any]) -> GarageSettings:
        """
        Override of the default `create()`-method, for allowing  the post of nested
        JSON-objects. First, a `Locations`-object is created, whereafter a
        `GarageSettings`-object is created with the `Locations`-object created earlier.
        """
        locationData = validated_data.pop("location")
        location = Locations.objects.create(**locationData)
        return GarageSettings.objects.create(location=location, **validated_data)

    def update(self, validated_data: dict[str, Any]) -> GarageSettings:
        """
        Override of the default `update()`-method, for allowing  the post of nested
        JSON-objects. First, a `Locations`-object is created, whereafter a
        `GarageSettings`-object is created with the `Locations`-object created earlier.
        """
        locationData = validated_data.pop("location")
        location = Locations.objects.create(**locationData)
        return GarageSettings.objects.create(location=location, **validated_data)

    class Meta:
        model = GarageSettings
        fields = [
            "id",
            "location",
            "maxHeight",
            "maxWidth",
            "maxHandicappedLots",
        ]
