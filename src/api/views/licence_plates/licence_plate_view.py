from django.http import Http404

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request

from src.api.models import LicencePlate
from src.api.serializers import LicencePlateSerializer, PostLicencePlateSerializer
from src.core.views import BackendResponse, GetObjectMixin, _OriginAPIView


class LicencePlateListView(_OriginAPIView, GetObjectMixin):
    """
    Returns a list of the licence plates belonging to a user.
    """

    origins = ["app", "web"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().put(request, format)) is not None:
            return resp

        licence_plates = LicencePlate.objects.filter(user=request.user)

        serializer = LicencePlateSerializer(licence_plates, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)



class LicencePlateDetailView(_OriginAPIView, GetObjectMixin):
    """
    Update a `LicencePlate` with the given `pk`.
    """

    origins = ["app", "web"]

    def put(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().put(request, format)) is not None:
            return resp
        licence_plate_data = JSONParser().parse(request)
        try:
            licence_plate = self.get_object(LicencePlate, pk)
        except Http404:
            return BackendResponse(
                [f"The given licence plate with id {pk} does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LicencePlateSerializer(licence_plate, data=licence_plate_data)
        if serializer.is_valid():
            serializer.save()
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
