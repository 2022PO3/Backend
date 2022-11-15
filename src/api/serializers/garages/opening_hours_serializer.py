from rest_framework import serializers
from src.api.models import OpeningHours


class OpeningHoursSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage_id")
    dayFrom = serializers.IntegerField(source="day_from")
    dayTo = serializers.IntegerField(source="day_to")
    hourFrom = serializers.DateTimeField(source="hour_from")
    hourTo = serializers.DateTimeField(source="hour_to")

    class Meta:
        model = OpeningHours
        fields = ["id", "garageId", "dayFrom", "dayTo", "hourFrom", "hourTo"]
