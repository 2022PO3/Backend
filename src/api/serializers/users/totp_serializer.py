from rest_framework import serializers

from django_otp.plugins.otp_totp.models import TOTPDevice


class TOTPSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing GET-, POST-, PUT- requests of TOTP devices.
    """

    class Meta:
        model = TOTPDevice
        fields = ["id", "name", "confirmed"]
        extra_kwargs = {"confirmed": {"read_only": True}}
