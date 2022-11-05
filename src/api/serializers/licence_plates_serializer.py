from rest_framework import serializers
from src.api.models import LicencePlates


class LicencePlatesSerializer(serializers.ModelSerializer):
    licencePlate = serializers.CharField(source="licence_plate")
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = LicencePlates
        fields = ["id", "updatedAt", "user", "garage", "licencePlate"]
