from typing import Any

from rest_framework import serializers

from src.api.models import Garages, GarageSettings, Prices, Locations
from src.api.serializers import (
    GarageSettingsSerializer,
)
from src.core.serializers import APIBaseSerializer


class GetGaragesSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing GET-requests of garages.
    """

    ownerId = serializers.IntegerField(source="owner.pk")
    isFull = serializers.BooleanField(source="is_full", read_only=True)
    unoccupiedLots = serializers.IntegerField(source="unoccupied_lots", read_only=True)
    parkingLots = serializers.IntegerField(source="parking_lots", read_only=True)

    class Meta:
        model = Garages
        fields = [
            "id",
            "ownerId",
            "name",
            "isFull",
            "unoccupiedLots",
            "parkingLots",
        ]


class PostGaragesSerializer(APIBaseSerializer):
    """
    Serializer for serializing GET-requests of garages.
    """

    garage_settings = GarageSettingsSerializer()

    class Meta:
        model = Garages
        fields = ["id", "owner_id", "name", "garage_settings"]

    def create(self, validated_data: dict[str, Any]) -> Garages:
        """
        Override of the default `create()`-method, for allowing  the post of nested
        JSON-objects. First, a `Locations`-object is created, whereafter a
        `GarageSettings`-object is created with the `Locations`-object created earlier. Lastly,
        a `Garage`-object will be created with the two previously created models.
        """

        settingsData = validated_data.pop("garage_settings")
        locationData = settingsData.pop("location")
        location = Locations.objects.create(**locationData)
        garage_settings = GarageSettings.objects.create(
            location=location, **settingsData
        )
        garage = Garages.objects.create(
            garage_settings=garage_settings, **validated_data
        )
        return garage
