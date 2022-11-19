from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.api.models import ParkingLots
from src.api.serializers import ParkingLotsSerializer
from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.users.permissions import IsGarageOwner


class ParkingLotsListView(OriginAPIView):
    """
    A view class which renders all the parking lots for a given garage with `pk`.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            parking_lots = ParkingLots.objects.filter(garage_id=pk)
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ParkingLotsSerializer(parking_lots, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)


class ParkingLotsDetailView(OriginAPIView, GetObjectMixin):
    """
    A view class which renders a PUT-request for a parking lot with the given `pk`.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().put(request, format)) is not None:
            return resp
        parking_lot_data = JSONParser().parse(request)
        serializer = ParkingLotsSerializer(data=parking_lot_data)
        if serializer.is_valid():
            parking_lot = serializer.save()
            self.check_object_permissions(request, parking_lot)
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().put(request, format)) is not None:
            return resp
        try:
            parking_lot = self.get_object(ParkingLots, pk)
        except Http404:
            return BackendResponse(
                [f"The parking lot with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        parking_lot_data = JSONParser().parse(request)
        serializer = ParkingLotsSerializer(parking_lot, data=parking_lot_data)
        if serializer.is_valid():
            parking_lot = serializer.save()
            self.check_object_permissions(request, parking_lot)
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
