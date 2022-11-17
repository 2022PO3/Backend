from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import Garages
from src.api.serializers import GaragesSerializer


class GarageDetailView(GetObjectMixin, OriginAPIView):
    """
    A view class which incorporates the views regarding single instances of the
    `Garage`-model, which makes it possible to query a single garage on `pk`.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            garage = self._get_object(Garages, pk)
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = GaragesSerializer(garage)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)


class GarageListView(OriginAPIView):
    """
    A view class to get all the garages and to post a new garage.
    """

    origins = ["app", "web"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        garages = Garages.objects.all()
        serializer = GaragesSerializer(garages, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        garage_data = JSONParser().parse(request)
        garages_serializer = GaragesSerializer(data=garage_data)
        if garages_serializer.is_valid():
            garages_serializer.save()
            return BackendResponse(
                garages_serializer.data, status=status.HTTP_201_CREATED
            )
        return BackendResponse(
            garages_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
