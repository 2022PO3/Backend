from django.http import Http404

from rest_framework import status
from rest_framework.request import Request

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import OpeningHours
from src.api.serializers import OpeningHoursSerializer


class OpeningHoursView(OriginAPIView, GetObjectMixin):
    """
    A view class which renders the settings for a given garage. These include all fields from the `GarageSettings`-model, as well as the location and opening hours of the Garage. See the API-documentation for more details.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            garage_opening_hours = OpeningHours.objects.filter(garage_id=pk)
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = OpeningHoursSerializer(garage_opening_hours, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
