from typing import Any
from collections import OrderedDict

from rest_framework import serializers
from src.api.models import Reservation, parking_lot_is_available, ParkingLot
from src.api.serializers import GarageSerializer
from src.core.serializers import APIForeignKeySerializer


class GetReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing both GET and POST requests of the current user's reservations.
    """

    garage = GarageSerializer()
    user_id = serializers.IntegerField()
    parking_lot_id = serializers.IntegerField()

    class Meta:
        model = Reservation
        fields = ["id", "garage", "user_id", "parking_lot_id", "from_date", "to_date"]
        readonly_field = ["user_id"]


class PostReservationSerializer(APIForeignKeySerializer):
    garage_id = serializers.IntegerField()
    parking_lot_id = serializers.IntegerField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """
        Check that `fromDate` is before `finish`.
        """
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
        fields = ["id", "garage_id", "parking_lot_id", "from_date", "to_date"]


class AssignReservationSerializer(APIForeignKeySerializer):
    """
    Serializer class which serializes responses which assign a random free parking lot to the user. Note that the reservation will not be recorded  before they made a call to the reservations view.
    """

    garage_id = serializers.IntegerField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        if data["from_date"] > data["to_date"]:
            raise serializers.ValidationError("`from_date` must occur before `to_date`")
        return super().validate(data)

    class Meta:
        model = Reservation
        fields = ["garage_id", "from_date", "to_date"]
