from typing import Any

from rest_framework import serializers

from src.api.models import GarageSettings, Locations
from src.api.serializers import LocationsSerializer


class GetGarageSettingsSerializer(serializers.ModelSerializer):
    location = LocationsSerializer(read_only=True)
    maxHeight = serializers.FloatField(source="max_height")
    maxWidth = serializers.FloatField(source="max_width")
    maxHandicappedLots = serializers.IntegerField(source="max_handicapped_lots")

    class Meta:
        model = GarageSettings
        fields = [
            "id",
            "location",
            "maxHeight",
            "maxWidth",
            "maxHandicappedLots",
        ]


class PostGarageSettingsSerializer(serializers.ModelSerializer):
    location = LocationsSerializer()
    maxHeight = serializers.FloatField(source="max_height")
    maxWidth = serializers.FloatField(source="max_width")
    maxHandicappedLots = serializers.IntegerField(source="max_handicapped_lots")

    class Meta:
        model = GarageSettings
        fields = [
            "location",
            "maxHeight",
            "maxWidth",
            "maxHandicappedLots",
        ]

    def create(self, validated_data: dict[str, Any]) -> GarageSettings:
        locationData = validated_data.pop("location")
        Locations.objects.create(**locationData)
        return GarageSettings.objects.create(**validated_data)
