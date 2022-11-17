from rest_framework import serializers
from src.api.serializers import GaragesSerializer
from src.api.models import Reservations


class GetReservationsSerializer(serializers.ModelSerializer):
    garage = GaragesSerializer(read_only=True)
    userId = serializers.IntegerField(source="user.pk")
    parkingLotId = serializers.IntegerField(source="parking_lot.pk")
    fromDate = serializers.DateTimeField(source="from_date")
    toDate = serializers.DateTimeField(source="to_date")

    class Meta:
        model = Reservations
        fields = ["id", "garage", "userId", "parkingLotId", "fromDate", "toDate"]


class PostReservationsSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage_id")
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
        fields = ["garageId", "parkingLotId", "fromDate", "toDate"]
