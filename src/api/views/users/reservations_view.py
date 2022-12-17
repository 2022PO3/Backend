from random import randint
from typing import Any
from rest_framework import status
from rest_framework.request import Request

from src.api.models import ParkingLot, Reservation
from src.api.serializers import (
    ParkingLotSerializer,
    AssignReservationSerializer,
    GetReservationSerializer,
    PostReservationSerializer,
    ReservationRPiSerializer,
)

from src.core.views import _OriginAPIView, BackendResponse
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
    post_user_id = True


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
    serializer = ReservationRPiSerializer
    model = Reservation
