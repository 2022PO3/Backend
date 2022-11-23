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
        ]


class GetAvailableParkingLotsSerializer(APIForeignKeySerializer):
    """
    Serializer for handling requests which demand only the available parking lots of given garage.
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


class RPIParkingLotSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing request coming from the Raspberry Pi to update a parking lot.
    """

    garage_id = serializers.IntegerField()

    class Meta:
        model = ParkingLot
        fields = ["id", "garage_id", "parking_lot_no"]
