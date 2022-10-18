from rest_framework import serializers
from src.api.models.garages import Garages


class GaragesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garages
        fields = ["id", "owner_id", "is_full", "unoccupied_lots"]
