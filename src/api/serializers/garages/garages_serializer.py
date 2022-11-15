from rest_framework import serializers

from src.api.models import Garages


class LocationsSerializer(serializers.ModelSerializer):
    postCode = serializers.BooleanField(source="post_code", read_only=True)

    class Meta:
        model = Garages
        fields = [
            "id",
            "country",
            "province",
            "municipality",
            "postCode",
            "street",
            "number",
        ]
