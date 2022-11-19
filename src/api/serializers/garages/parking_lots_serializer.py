from rest_framework import serializers
from src.core.serializers import APIBaseSerializer
from src.api.models import ParkingLots


class ParkingLotsSerializer(APIBaseSerializer):
    """
    Serializer for serializing GET-requests of parking lots.
    """

    model = ParkingLots
    field_names = ["id", "occupied", "disabled", "garageId"]
