from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.api.models import GarageSettings
from src.api.serializers import LocationsSerializer
from src.core.views import BackendResponse, GetObjectMixin, _OriginAPIView
from src.users.permissions import IsGarageOwner


class LocationsView(_OriginAPIView, GetObjectMixin):
    """
    A view class which renders the settings for a given garage with `pk`. These include all fields from the `GarageSettings`-model, as well as the location.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp
        try:
            location = self.get_object(GarageSettings, pk).location
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LocationsSerializer(location)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        locations_data = JSONParser().parse(request)
        locations_serializer = LocationsSerializer(data=locations_data)
        if locations_serializer.is_valid():
            location = locations_serializer.save()
            # self.check_object_permissions(request, garage)
            return BackendResponse(
                locations_serializer.data, status=status.HTTP_201_CREATED
            )
        return BackendResponse(
            locations_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
