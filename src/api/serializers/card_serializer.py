from rest_framework import serializers

from src.api.models.card import Card


class CardSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing GET-requests of licence plates.
    """

    class Meta:
        model = Card
        fields = ["number", "exp_month", "exp_year", "cvc"]

