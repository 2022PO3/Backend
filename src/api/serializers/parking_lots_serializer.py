from rest_framework import serializers
from src.api.models import ParkingLots


class ParkingLotsSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage_id")
    floorNumber = serializers.IntegerField(source="floor_number")

    class Meta:
        model = ParkingLots
        fields = ["id", "garageId", "floorNumber", "occupied"]
