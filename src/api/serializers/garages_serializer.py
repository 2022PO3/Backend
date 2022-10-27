from rest_framework import serializers
from src.api.models.garages import Garages
from src.api.models.parking_lots import ParkingLots


class GaragesSerializer(serializers.ModelSerializer):
    isFull = serializers.BooleanField(source="is_full")
    unoccupiedLots = serializers.IntegerField(source="unoccupied_lots")
    parkingLots = serializers.IntegerField(source="parking_lots")

    class Meta:
        model = Garages
        fields = [
            "id",
            "owner",
            "name",
            "isFull",
            "unoccupiedLots",
            "parkingLots",
        ]

    def to_representation(self, instance) -> Any:
        self.fields["owner"] = UserSerializer(read_only=True)
        return super().to_representation(instance)
