from typing import Any

from rest_framework import serializers

from src.api.models import Garages, GarageSettings, Prices, Locations
from src.api.serializers import (
    PostPricesSerializer,
    PostGarageSettingsSerializer,
)


class GetGaragesSerializer(serializers.ModelSerializer):
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


class PostGaragesSerializer(serializers.ModelSerializer):
    ownerId = serializers.IntegerField(source="owner_id")
    garageSettings = PostGarageSettingsSerializer(source="garage_settings")

    class Meta:
        model = Garages
        fields = ["id", "ownerId", "name", "garageSettings"]

    def create(self, validated_data: dict[str, Any]) -> Garages:
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
