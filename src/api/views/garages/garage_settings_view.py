from django.http import Http404

from rest_framework import status
from rest_framework.request import Request

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import Garages
from src.api.serializers import PostGarageSettingsSerializer


class GarageSettingsView(OriginAPIView, GetObjectMixin):
    """
    A view class which renders the settings for a given garage with `pk`. These include all fields from the `GarageSettings`-model, as well as the location.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            garage_settings = self._get_object(Garages, pk).garage_settings
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist."],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PostGarageSettingsSerializer(garage_settings)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
