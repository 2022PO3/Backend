from rest_framework import serializers
from src.api.models import Price
from src.core.serializers import APIForeignKeySerializer


class PriceSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing requests for prices.
    """

    garage_id = serializers.IntegerField()

    class Meta:
        model = Price
        fields = ["id", "garage_id", "price_string", "price", "valuta"]
