from django.http import Http404

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlates
from src.api.serializers import LicencePlatesSerializer, PostLicencePlateSerializer
from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView


class RPiLicencePlateView(OriginAPIView):
    """
    A view class to get all the licence plates.
    """

    permission_classes = [AllowAny]
    origins = ["rpi"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        licence_plate_data = JSONParser().parse(request)
        licence_plate_serializer = PostLicencePlateSerializer(data=licence_plate_data)
        if licence_plate_serializer.is_valid():
            LicencePlates.handle_licence_plate(
                licence_plate_serializer.data,
            )
            return BackendResponse(
                licence_plate_serializer.data, status=status.HTTP_201_CREATED
            )
        return BackendResponse(
            licence_plate_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LicencePlateDetailView(OriginAPIView, GetObjectMixin):
    """
    Update a `LicencePlate` with the given `pk`.
    """

    origins = ["app", "web"]

    def put(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().put(request, format)) is not None:
            return resp
        licence_plate_data = JSONParser().parse(request)
        try:
            licence_plate = self.get_object(LicencePlates, pk)
        except Http404:
            return BackendResponse(
                [f"The given licence plate with id {pk} does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LicencePlatesSerializer(licence_plate, data=licence_plate_data)
        if serializer.is_valid():
            serializer.save()
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
