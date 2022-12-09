from typing import Any
from collections import OrderedDict

from rest_framework import serializers
from src.api.models import (
    Reservation,
    parking_lot_is_available,
    ParkingLot,
    LicencePlate,
)
from src.api.serializers import (
    GarageSerializer,
    ParkingLotSerializer,
    LicencePlateSerializer,
)
from src.core.serializers import APIForeignKeySerializer


class GetReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing both GET and POST requests of the current user's reservations.
    """

    garage = GarageSerializer()
    licence_plate = LicencePlateSerializer()
    parking_lot = ParkingLotSerializer()

    class Meta:
        model = Reservation
        fields = [
            "id",
            "user_id",
            "garage",
            "licence_plate",
            "parking_lot",
            "from_date",
            "to_date",
        ]


class PostReservationSerializer(APIForeignKeySerializer):
    user_id = serializers.IntegerField()
    garage_id = serializers.IntegerField()
    licence_plate_id = serializers.IntegerField()
    parking_lot_id = serializers.IntegerField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """
        Check that `fromDate` is before `finish`.
        """
        user_reservations = Reservation.objects.filter(
            licence_plate=data["licence_plate_id"]
        )
        if data["from_date"] > data["to_date"]:
            raise serializers.ValidationError("`fromDate` must occur before `toDate`")
        if not parking_lot_is_available(
            ParkingLot.objects.get(id=data["parking_lot_id"]),
            data["from_date"],
            data["to_date"],
        ):
            raise serializers.ValidationError(
                "The parking lot is already occupied on that day and time, please choose another one."
            )
        return super().validate(data)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "user_id",
            "garage_id",
            "licence_plate_id",
            "parking_lot_id",
            "from_date",
            "to_date",
        ]


class AssignReservationSerializer(APIForeignKeySerializer):
    """
    Serializer class which serializes responses which assign a random free parking lot to the user. Note that the reservation will not be recorded  before they made a call to the reservations view.
    """

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        if data["from_date"] > data["to_date"]:
            raise serializers.ValidationError("`from_date` must occur before `to_date`")
        return super().validate(data)

    class Meta:
        model = Reservation
        fields = ["from_date", "to_date"]
