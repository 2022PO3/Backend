from rest_framework import serializers

from django_otp.plugins.otp_totp.models import TOTPDevice


class GetTOTPSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing get requests of user's TOTP devices.
    """

    class Meta:
        model = TOTPDevice
        fields = ["id", "user_id", "name", "confirmed"]


class PostTOTPSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing creation request of a TOTP device.
    """

    class Meta:
        model = TOTPDevice
        fields = ["name"]
