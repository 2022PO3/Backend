from rest_framework import serializers
from src.api.models.garages import Garages
from src.api.models.parking_lots import ParkingLots


class GaragesSerializer(serializers.ModelSerializer):
    ownerId = serializers.IntegerField(source="owner_id")
    isFull = serializers.BooleanField(source="is_full")
    unoccupiedLots = serializers.IntegerField(source="unoccupied_lots")
    parkingLots = serializers.IntegerField(source="parking_lots")

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
