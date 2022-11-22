from typing import Any
from collections import OrderedDict

from rest_framework import serializers

from src.api.models import OpeningHour
from src.api.models import DaysOfTheWeekEnum
from src.core.serializers import APIForeignKeySerializer


class OpeningHourSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing GET-requests of the opening hours.
    """

    garage_id = serializers.IntegerField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """
        Check that start is before finish and that the `toDay` and `fromDay`-field in the
        requests contain only values of the `DayOfTheWeekEnum`.
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
        return super().validate(data)

    class Meta:
        model = OpeningHour
        fields = ["garage_id", "from_day", "to_day", "from_hour", "to_hour"]
