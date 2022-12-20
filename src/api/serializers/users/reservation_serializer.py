from typing import Any
from collections import OrderedDict
from datetime import datetime

from rest_framework import serializers
from src.api.models import (
    Reservation,
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
            "garage",
            "licence_plate",
            "parking_lot",
            "from_date",
            "to_date",
        ]


class PostReservationSerializer(APIForeignKeySerializer):
    garage_id = serializers.IntegerField()
    licence_plate_id = serializers.IntegerField()
    parking_lot_id = serializers.IntegerField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """
        Check that `fromDate` is before `finish`.
        """
        from_date: datetime = data["from_date"]
        to_date: datetime = data["to_date"]
        lp_id: int = data["licence_plate_id"]
        lp = LicencePlate.objects.get(pk=lp_id)
        if not lp.can_reserve(from_date, to_date):
            raise serializers.ValidationError(
                "This licence plate already has a reservation that time."
            )
        if not lp.enabled:
            raise serializers.ValidationError("Licence plate is not confirmed.")
        if from_date > to_date:
            raise serializers.ValidationError("`fromDate` must occur before `toDate`")
        parking_lot: ParkingLot = ParkingLot.objects.get(id=data["parking_lot_id"])
        if not parking_lot.available(
            from_date,
            to_date,
        ):
            raise serializers.ValidationError(
                "The parking lot is already occupied on that day and time, please choose another one."
            )
        return super().validate(data)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "garage_id",
            "licence_plate_id",
            "parking_lot_id",
            "from_date",
            "to_date",
        ]


class ReservationRPiSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing GET-requests of the RPi.
    """

    parking_lot = ParkingLotSerializer()

    class Meta:
        model = Reservation
        fields = ["parking_lot", "from_date", "to_date", "is_valid"]


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
