from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from src.core.views import BackendResponse
from src.core.utils import OriginAPIView
from src.api.models import Garages
from src.api.serializers import GaragesSerializer


class GarageDetailView(OriginAPIView):
    """
    A view class which incorporates the views regarding single instances of the `Garage`-model:
    - get a single garage by `id`;
    - post a new garage.
    """

    origins = ["app", "web"]

    def get_object(self, pk):
        try:
            return Garages.objects.get(pk=pk)
        except Garages.DoesNotExist:
            raise Http404


class GarageListView(OriginAPIView):
    """
    A view class to get all the garages.
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
