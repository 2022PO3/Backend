from collections import OrderedDict
from typing import Any

from rest_framework import serializers
from src.api.models import Price
from src.core.serializers import APIForeignKeySerializer
from src.core.utils.stripe_endpoints import get_stripe_price


class PriceSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing requests for prices.
    """

    garage_id = serializers.IntegerField(source="garage_id")

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """Check if the data on the Stripe server is the same as on ours"""
        stripe_price = get_stripe_price(data['stripe_identifier'])

        if stripe_price is None:
            raise serializers.ValidationError("This price id doesn't exist in the Stripe database, so we can't use it for payments.")
        if stripe_price['unit_amount']/100 != data['price']:
            serializers.ValidationError("The price amount does not match the one in the Stripe database.")
        if stripe_price['currency'] != data['valuta']:
            raise serializers.ValidationError("The currency does not match the one in the Stripe database.")

        return super().validate(data)

    class Meta:
        model = Price
        fields = ["id", "garage_id", "price_string", "duration", "price", "valuta", 'stripe_identifier']

class CreatePriceSerializer(APIForeignKeySerializer):

    garage_id = serializers.IntegerField(source="garage_id")

    class Meta:
        model = Price
        fields = ["id", "garage_id", "price_string", "duration", "price", "valuta"]

