from rest_framework import serializers
from src.api.serializers import GetGaragesSerializer
from src.api.models import Reservations


class ReservationsSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing both GET and POST requests of the current user's reservations.
    """

    garage = GetGaragesSerializer(read_only=True)
    userId = serializers.IntegerField(source="user_id")
    parkingLotId = serializers.IntegerField(source="parking_lot_id")
    fromDate = serializers.DateTimeField(source="from_date")
    toDate = serializers.DateTimeField(source="to_date")

    def validate(self, data):
        """
        Check that `fromDate` is before `finish`.
        """
        if data["from_date"] > data["to_date"]:
            raise serializers.ValidationError("`fromDate` must occur before `toDate`")
        return data

    class Meta:
        model = Reservations
        fields = ["id", "garage", "userId", "parkingLotId", "fromDate", "toDate"]
