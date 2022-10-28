from rest_framework import serializers
from src.api.models.licence_plates import LicencePlates


class LicencePlatesSerializer(serializers.ModelSerializer):
    licencePlate = serializers.CharField(source="licence_plate")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = LicencePlates
        fields = ["id", "updatedAt", "user", "garage", "licencePlate"]
        extra_kwargs = {"updatedAt": {"read_only": True}}
