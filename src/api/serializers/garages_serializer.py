from rest_framework import serializers
from src.api.models.garages import Garage


class GarageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garage
        fields = ["id", "owner_id"]
