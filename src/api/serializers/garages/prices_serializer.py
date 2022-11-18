from rest_framework import serializers
from src.api.models import Prices


class PricesSerializer(serializers.ModelSerializer):
    garageId = serializers.IntegerField(source="garage_pk")
    priceString = serializers.CharField(source="price_string")

    class Meta:
        model = Prices
        fields = ["id", "garageId", "priceString", "price", "valuta"]
