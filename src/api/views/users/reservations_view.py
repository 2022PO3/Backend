from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.models import Reservation
from src.api.serializers import (
    GetReservationSerializer,
    PostReservationSerializer,
    ReservationRPiSerializer,
)

from src.core.views import BackendResponse, parse_frontend_json
from src.core.views import BaseAPIView, PkAPIView
from src.users.permissions import IsUserReservation


class ReservationsListView(BaseAPIView):
    """
    View class which handles GET- and POST-requests for the user's reservation..
    """

    origins = ["app", "web"]
    serializer = {
        "get": GetReservationSerializer,
        "post": PostReservationSerializer,
    }
    model = Reservation
    get_user_id = True

    def post(self, request: Request, format=None) -> BackendResponse | None:
        data = parse_frontend_json(request)
        serializer = PostReservationSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            garage_id: int = serializer.validated_data["garage_id"]  # type: ignore
            serializer.save(user=request.user)
            return BackendResponse(serializer.data, status=status.HTTP_201_CREATED)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationsDetailView(PkAPIView):
    """
    View class which handles PUT- and DELETE-requests for a reservation with `pk`.
    """

    origins = ["app", "web"]
    permission_classes = [IsUserReservation]
    serializer = PostReservationSerializer
    model = Reservation


class ReservationsRPiView(PkAPIView):
    """
    View class which handles GET-requests for reservations of the garage the RPi is located in.
    """

    origins = ["rpi"]
    permission_classes = [AllowAny]
    serializer = ReservationRPiSerializer
    model = Reservation
    return_list = True
    http_method_names = ["get"]
    column = "garage_id"

    def get(self, request: Request, garage_pk: int, format=None) -> BackendResponse:
        return super().get(request, garage_pk, format)
