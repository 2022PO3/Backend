from rest_framework import serializers
from src.api.models import ParkingLots


class SettingsSerializer(serializers.ModelSerializer):
    favGarageId = serializers.IntegerField(source="fav_garage_id")

    class Meta:
        model = ParkingLots
        fields = ["id", "favGarageId", "location"]
