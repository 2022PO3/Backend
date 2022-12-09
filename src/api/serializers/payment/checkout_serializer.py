from rest_framework import serializers
from src.api.models import LicencePlate


class CheckoutSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing the POST-requests for a specific licence plate on the payment endpoints.
    """

    licence_plate = serializers.CharField()

    class Meta:
        model = LicencePlate
        fields = ["licence_plate"]
