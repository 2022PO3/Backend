from rest_framework import serializers
from src.core.serializers import APIBaseSerializer
from src.api.models import ParkingLots


class ParkingLotsSerializer(APIBaseSerializer):
    """
    Serializer for serializing GET-requests of parking lots.
    """

    class Meta:
        model = ParkingLots
        fields = ["id", "garage_id", "floor_number", "occupied", "disabled"]
