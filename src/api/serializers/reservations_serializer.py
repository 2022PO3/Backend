from rest_framework import serializers
from src.api.models import ParkingLots


class ReservationsSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage")
    userId = serializers.IntegerField(source="user")
    parkingLotId = serializers.IntegerField(source="parking_lot")
    fromDate = serializers.DateTimeField()
    toDate = serializers.DateTimeField()

    class Meta:
        model = ParkingLots
        fields = ["id", "garageId", "userId", "parkingLotId", "fromDate", "toDate"]
