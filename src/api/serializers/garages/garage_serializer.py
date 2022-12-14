from typing import Any

from src.api.models import Garage, GarageSettings, Location
from src.api.serializers import GarageSettingsSerializer
from src.core.serializers import APIForeignKeySerializer


class GarageSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing GET-requests of garages.
    """

    garage_settings = GarageSettingsSerializer()

    def create(self, validated_data: dict[str, Any]) -> Garage:
        """
        Override of the default `create()`-method, for allowing  the post of nested
        JSON-objects. First, a `Locations`-object is created, whereafter a
        `GarageSettings`-object is created with the `Locations`-object created earlier. Lastly,
        a `Garage`-object will be created with the two previously created models.
        """
        settings_data = validated_data.pop("garage_settings")
        location_data = settings_data.pop("location")
        location = Location.objects.create(**location_data)
        garage_settings = GarageSettings.objects.create(
            location=location, **settings_data
        )
        garage = Garage.objects.create(
            garage_settings=garage_settings, **validated_data
        )
        return garage

    def update(self, instance: Garage, validated_data: dict[str, Any]) -> Garage:
        settings_data = validated_data.pop("garage_settings")
        location_data = settings_data.pop("location")
        super().update(instance.garage_settings.location, location_data)
        super().update(instance.garage_settings, settings_data)
        return super().update(instance, validated_data)

    class Meta:
        model = Garage
        fields = [
            "id",
            "name",
            "user_id",
            "is_full",
            "unoccupied_lots",
            "parking_lots",
            "garage_settings",
        ]
        read_only_fields = ["is_full", "unoccupied_lots", "parking_lots", "user_id"]
