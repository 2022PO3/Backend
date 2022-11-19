import re
from functools import reduce
from rest_framework import serializers
from django.db.models import Model
from typing import OrderedDict, TypeVar, Any

T = TypeVar("T", bound=Model)


class APIBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer class from which all serializers for API models should inherit from. It
    converts all field from snake_case to lowerCamelCase with the correct source attribute.
    """

    def to_internal_value(self, data: dict[str, Any]) -> OrderedDict:
        data_copy = data.copy()
        for key in data.keys():
            if re.search(r"[A-Z]", key):
                snake_case_key = to_snake_case(key)
                data_copy[snake_case_key] = data_copy.pop(key)
        print(data_copy)
        return super(APIBaseSerializer, self).to_internal_value(data_copy)

    def to_representation(self, instance: T) -> OrderedDict:
        data = super(APIBaseSerializer, self).to_representation(instance)
        data_copy = data.copy()
        for key in data.keys():
            if "_" in key:
                camel_case_string = to_camel_case(key)
                data_copy[camel_case_string] = data_copy.pop(key)
        return data_copy


def to_camel_case(string: str) -> str:
    init, *temp = string.split("_")
    return "".join([init.lower(), *map(str.title, temp)])


def to_snake_case(string: str) -> str:
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, string).lower()
