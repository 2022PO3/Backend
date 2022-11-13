from rest_framework import serializers
from src.api.models import LicencePlates


class LicencePlatesSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage_id")
    licencePlate = serializers.CharField(source="licence_plate")
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = LicencePlates
        fields = ["id", "updatedAt", "userId", "garageId", "licencePlate"]


class PostLicencePlateSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing PUT requests (only the `licence_plate` and the `garage` have to be given with the request).
    """

    garageId = serializers.IntegerField(source="garage_id")
    licencePlate = serializers.CharField(source="licence_plate")

    class Meta:
        model = LicencePlates
        fields = ["garageId", "licencePlate"]
