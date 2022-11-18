from typing import Any

from rest_framework import serializers

from src.api.models import Garages, GarageSettings, Prices
from src.api.serializers import (
    LocationsSerializer,
    PostOpeningHoursSerializer,
    PricesSerializer,
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
    ownerId = serializers.IntegerField(source="owner_pk")
    prices = PricesSerializer(many=True)
    settings = PostGarageSettingsSerializer()

    class Meta:
        model = Garages
        field = ["ownerId", "name", "prices", "settings"]

    def create(self, validated_data: dict[str, Any]) -> Garages:
        prices_data = validated_data.pop("prices")
        settingsData = validated_data.pop("settings")
        GarageSettings.objects.create(**settingsData)
        garage = Garages.objects.create(**validated_data)
        for price_data in prices_data:
            Prices.objects.create(garage=garage, **price_data)
        return garage
