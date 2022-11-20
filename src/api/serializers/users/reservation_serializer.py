from collections import OrderedDict
from typing import Any
from rest_framework import serializers
from src.api.serializers import GarageSerializer
from src.api.models import Reservation
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


class PostReservationSerializer(APIForeignKeySerializer):
    garage_id = serializers.IntegerField()
    parking_lot_id = serializers.IntegerField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """
        Check that `fromDate` is before `finish`.
        """
        if data["from_date"] > data["to_date"]:
            raise serializers.ValidationError("`fromDate` must occur before `toDate`")
        return super().validate(data)

    class Meta:
        model = Reservation
        fields = ["id", "garage_id", "parking_lot_id", "from_date", "to_date"]
