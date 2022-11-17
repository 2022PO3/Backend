from rest_framework import serializers

from src.api.models import OpeningHours
from src.api.models import DaysOfTheWeekEnum


class GetOpeningHoursSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage.pk")
    fromDay = serializers.IntegerField(source="from_day")
    toDay = serializers.IntegerField(source="to_day")
    fromHour = serializers.DateTimeField(source="from_hour")
    toHour = serializers.DateTimeField(source="to_hour")

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if data["start"] > data["finish"]:
            raise serializers.ValidationError("finish must occur after start")
        return data

    class Meta:
        model = OpeningHours
        fields = ["id", "garageId", "fromDay", "toDay", "fromHour", "toHour"]


class PostOpeningHoursSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage_id")
    fromDay = serializers.IntegerField(source="from_day")
    toDay = serializers.IntegerField(source="to_day")
    fromHour = serializers.TimeField(source="from_hour")
    toHour = serializers.TimeField(source="to_hour")

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if data["from_day"] > data["to_day"]:
            raise serializers.ValidationError("`from_date` must occur before `to_date`")
        if data["from_hour"] > data["to_hour"]:
            raise serializers.ValidationError("`from_hour` must occur before `to_hour`")
        if data["from_day"] not in DaysOfTheWeekEnum.values:
            raise serializers.ValidationError(
                f"The value of `from_day` has to be one of {DaysOfTheWeekEnum.values}"
            )
        if data["from_day"] not in DaysOfTheWeekEnum.values:
            raise serializers.ValidationError(
                f"The value of `to_day` has to be one of {DaysOfTheWeekEnum.values}"
            )
        return data

    class Meta:
        model = OpeningHours
        fields = ["garageId", "fromDay", "toDay", "fromHour", "toHour"]
