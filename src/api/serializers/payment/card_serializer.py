from django.utils import timezone
from rest_framework import serializers


class CreditCardSerializer(serializers.Serializer):
    """
    Serializer for serializing GET-requests of credit cards plates.
    """

    number = serializers.CharField(max_length=19)
    exp_month = serializers.IntegerField(min_value=0, max_value=12)
    exp_year = serializers.IntegerField(min_value=timezone.now().year - 1)
    cvc = serializers.CharField(max_length=3)
