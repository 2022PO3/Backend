from rest_framework import serializers
from src.api.models.parking_lots import ParkingLot


class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ["id", "garage_id", "floor_number", "occupied"]
