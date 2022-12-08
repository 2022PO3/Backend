from random import randint
from rest_framework import status
from rest_framework.request import Request

from src.api.models import ParkingLot, Reservation
from src.api.serializers import (
    ParkingLotSerializer,
    AssignReservationSerializer,
    GetReservationSerializer,
    PostReservationSerializer,
)

from src.core.views import _OriginAPIView, BackendResponse
from src.core.views import BaseAPIView, PkAPIView
from src.users.permissions import IsUserReservation


class ReservationsView(BaseAPIView):
    """
    A view class to get all reservations from the currently logged in user and to post new one.
    The post method is overwritten as a
    """

    origins = ["app", "web"]
    serializer = {"get": GetReservationSerializer, "post": PostReservationSerializer}
    model = Reservation


class PutReservationsView(PkAPIView):
    origins = ["app", "web"]
    permission_classes = [IsUserReservation]
    serializer = PostReservationSerializer
    model = Reservation


class AssignReservationView(_OriginAPIView):
    origins = ["web", "app"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := _OriginAPIView.get(self, request, format)) is not None:
            return resp
        request_data = {
            "from_date": str(request.query_params["fromDate"]).replace(" ", "+"),
            "to_date": str(request.query_params["toDate"]).replace(" ", "+"),
        }
        assignment_serializer = AssignReservationSerializer(data=request_data)  # type: ignore
        if assignment_serializer.is_valid():
            valid_data = assignment_serializer.validated_data
            pls = list(
                filter(
                    lambda pl: not pl.booked,
                    ParkingLot.objects.is_available(
                        int(pk),
                        valid_data["from_date"],  # type: ignore
                        valid_data["to_date"],  # type: ignore
                    ),
                )
            )
            pl = pls[randint(0, len(pls))]
            serializer = ParkingLotSerializer(pl)
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            assignment_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
