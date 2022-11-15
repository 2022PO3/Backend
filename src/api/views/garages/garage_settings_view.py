from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import Garages, GarageSettings
from src.api.serializers import GarageSettingsSerializer


class GarageSettingsView(OriginAPIView, GetObjectMixin):
    """
    A view class which renders the settings for a given garage. These include all fields from the `GarageSettings`-model, as well as the location and opening hours of the Garage. See the API-documentation for more details.
    """

    origins = ["app", "web"]

    def get(self, pk: int, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        garage_settings = self.get_object_on_field(GarageSettings, "garage_id", pk)
        serializer = GarageSettingsSerializer(garage_settings, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
