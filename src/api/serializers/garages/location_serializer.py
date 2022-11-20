from rest_framework import serializers

from src.api.models import Location


class LocationsSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing both GET and POST-requests of locations.
    """

    class Meta:
        model = Location
        fields = "__all__"
