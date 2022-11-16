from rest_framework import serializers

from src.api.models import Locations


class LocationsSerializer(serializers.ModelSerializer):
    postCode = serializers.IntegerField(source="post_code")

    class Meta:
        model = Locations
        fields = [
            "id",
            "country",
            "province",
            "municipality",
            "postCode",
            "street",
            "number",
        ]
