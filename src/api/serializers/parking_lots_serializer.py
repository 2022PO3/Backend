from rest_framework import serializers
from src.api.models.parking_lots import ParkingLots


class ParkingLotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLots
        fields = ["id", "garage_id", "floor_number", "occupied"]
