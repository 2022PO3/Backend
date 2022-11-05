from rest_framework import serializers

from src.api.models.garages import Garages


class GaragesSerializer(serializers.ModelSerializer):
    isFull = serializers.BooleanField(source="is_full", read_only=True)
    unoccupiedLots = serializers.IntegerField(source="unoccupied_lots", read_only=True)
    parkingLots = serializers.IntegerField(source="parking_lots", read_only=True)

    class Meta:
        model = Garages
        fields = [
            "id",
            "owner",
            "name",
            "isFull",
            "unoccupiedLots",
            "parkingLots",
        ]
