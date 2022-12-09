from typing import OrderedDict, Any
from collections import OrderedDict

from rest_framework import serializers

import src.api.models
from src.core.utils import to_camel_case


class APIForeignKeySerializer(serializers.ModelSerializer):
    """
    Base serializer class which validates foreign key constraints in POST- or PUT-requests.
    """

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """
        Validates if all fields with suffix "_id" have an pk which exist in the database.
        """
        for key in data.keys():
            if "_id" in key and not "user" in key:
                self._validate_key(key, data[key])
        return super().validate(data)

    def _validate_key(self, key: str, value: Any) -> None:
        """
        Validates a single field with suffix "_id" and validates that the corresponding object with `pk=value` is present in the database.
        """
        if value is None:
            return
        class_name = to_camel_case(
            key.replace("_id", "").replace("fav_", ""), lower_case=False
        )
        klazz = eval(f"src.api.models.{class_name}")
        try:
            klazz.objects.get(pk=value)
        except klazz.DoesNotExist:
            raise serializers.ValidationError(
                f"{class_name} with `pk` {value} does not exist."
            )
