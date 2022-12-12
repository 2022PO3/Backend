from rest_framework import serializers
from src.api.models import LicencePlate
from src.core.serializers import APIForeignKeySerializer


class LicencePlateSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing GET-requests of licence plates.
    """

    class Meta:
        model = LicencePlate
        fields = [
            "id",
            "updated_at",
            "user_id",
            "garage_id",
            "enabled",
            "licence_plate",
        ]
        read_only_field = ["updated_at", "garage_id"]


class PostLicencePlateSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing POST requests (only the `licence_plate` and the `garage` have to be given with the request).
    """

    garage_id = serializers.IntegerField()
    licence_plate = serializers.CharField(max_length=7)

    class Meta:
        model = LicencePlate
        fields = ["garage_id", "licence_plate"]
