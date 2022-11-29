from rest_framework import serializers
from src.api.models import LicencePlate

class CheckoutSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing the login POST-requests for logging in users.
    """

    licence_plate = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = LicencePlate
        fields = ["licence_plate"]
