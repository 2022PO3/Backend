from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import OpeningHours
from src.api.serializers import GetOpeningHoursSerializer, PostOpeningHoursSerializer


class GetOpeningHoursView(OriginAPIView, GetObjectMixin):
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
        serializer = GetOpeningHoursSerializer(garage_opening_hours, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)


class PostOpeningHoursView(OriginAPIView):
    origins = ["app", "web"]

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp
        opening_hour = JSONParser().parse(request)
        opening_hours_serializer = PostOpeningHoursSerializer(data=opening_hour)
        if opening_hours_serializer.is_valid():
            opening_hours_serializer.save()
            return BackendResponse(
                opening_hours_serializer.data, status=status.HTTP_201_CREATED
            )
        return BackendResponse(
            opening_hours_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
