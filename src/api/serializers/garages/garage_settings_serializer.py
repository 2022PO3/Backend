from rest_framework import serializers
from src.api.models import GarageSettings


class GarageSettingsSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage_id")
    maxHeight = serializers.FloatField(source="max_height")
    maxWidth = serializers.FloatField(source="max_width")
    maxHandicappedLots = serializers.IntegerField(source="max_handicapped_lots")

    class Meta:
        model = GarageSettings
        fields = ["id", "garageId", "maxHeight", "maxWidth", "maxHandicappedLots"]
