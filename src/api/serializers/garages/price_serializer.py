from rest_framework import serializers
from src.api.models import Price


class PriceSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing requests for prices.
    """

    garage_id = serializers.IntegerField(source="garage_id")

    class Meta:
        model = Price
        fields = ["id", "garage_id", "price_string", "price", "valuta"]
