from rest_framework import serializers
from src.api.models import GarageSettings
from src.api.serializers import LocationsSerializer


class GarageSettingsSerializer(serializers.ModelSerializer):
    location = LocationsSerializer(read_only=True)
    maxHeight = serializers.FloatField(source="max_height")
    maxWidth = serializers.FloatField(source="max_width")
    maxHandicappedLots = serializers.IntegerField(source="max_handicapped_lots")

    class Meta:
        model = GarageSettings
        fields = [
            "id",
            "location",
            "maxHeight",
            "maxWidth",
            "maxHandicappedLots",
        ]
