from rest_framework import serializers
from src.api.models import OpeningHours


class OpeningHoursSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage.pk")
    fromDay = serializers.IntegerField(source="from_day")
    toDay = serializers.IntegerField(source="to_day")
    fromHour = serializers.DateTimeField(source="from_hour")
    toHour = serializers.DateTimeField(source="to_hour")

    class Meta:
        model = OpeningHours
        fields = ["id", "garageId", "fromDay", "toDay", "fromHour", "toHour"]
