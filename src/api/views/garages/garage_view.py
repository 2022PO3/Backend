from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import Garages
from src.api.serializers import GetGaragesSerializer, PostGaragesSerializer
from src.users.permissions import IsGarageOwner


class GarageDetailView(GetObjectMixin, OriginAPIView):
    """
    A view class which incorporates the views regarding single instance of the
    `Garage`-model, which makes it possible to query a single garage on `pk`.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            garage = self.get_object(Garages, pk)
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = GetGaragesSerializer(garage)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)


class GarageListView(OriginAPIView):
    """
    A view class to get all the garages and to post a new garage.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        garages = Garages.objects.all()
        serializer = GetGaragesSerializer(garages, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        garage_data = JSONParser().parse(request)
        garages_serializer = PostGaragesSerializer(data=garage_data)
        if garages_serializer.is_valid():
            garage = garages_serializer.save()
            self.check_object_permissions(request, garage)
            return BackendResponse(
                garages_serializer.data, status=status.HTTP_201_CREATED
            )
        return BackendResponse(
            garages_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
