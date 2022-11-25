from rest_framework import serializers

from src.api.models import ParkingLot
from src.core.serializers import APIForeignKeySerializer


class ParkingLotSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing requests of parking lots.
    """

    garage_id = serializers.IntegerField()

    class Meta:
        model = ParkingLot
        fields = [
            "id",
            "garage_id",
            "floor_number",
            "occupied",
            "disabled",
            "parking_lot_no",
            "booked",
        ]
        extra_kwargs = {"booked": {"allow_null": True}}


class RPIParkingLotSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing request coming from the Raspberry Pi to update a parking lot.
    """

    garage_id = serializers.IntegerField()

    class Meta:
        model = ParkingLot
        fields = ["id", "garage_id", "parking_lot_no", "occupied"]
