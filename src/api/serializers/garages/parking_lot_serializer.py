from rest_framework import serializers
from src.api.models import ParkingLot, Garage
from src.core.serializers import APIForeignKeySerializer


class ParkingLotSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing requests of parking lots.
    """

    garage_id = serializers.IntegerField()

    class Meta:
        model = ParkingLot
        fields = ["id", "garage_id", "floor_number", "occupied", "disabled"]
