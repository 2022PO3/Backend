from random import randint
from typing import Any
from dateutil.parser import parse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from src.api.models import ParkingLot
from src.api.serializers import ParkingLotSerializer, RPIParkingLotSerializer
from src.api.serializers import AssignReservationSerializer
from src.core.views import (
    PkAPIView,
    _OriginAPIView,
    parse_frontend_json,
    BackendResponse,
)
from src.users.permissions import IsGarageOwner


class ParkingLotDetailView(PkAPIView):
    """
    View class which handles PUT and DELETE-requests for a parking lot with `pk`.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    model = ParkingLot
    serializer = ParkingLotSerializer


class ParkingLotsGarageView(PkAPIView):
    """
    View class which handles GET- and POST-requests for parking lots of a garage with
    `garage_pk`.
    """

    origins = ["app", "web"]
    column = "garage_id"
    permission_classes = [IsGarageOwner]
    model = ParkingLot
    serializer = ParkingLotSerializer
    return_list = True
    http_method_names = ["get", "post"]

    def get(self, request: Request, garage_pk: int, format=None) -> BackendResponse:
        try:
            request_data = {
                "from_date": parse(str(request.query_params["fromDate"])),
                "to_date": parse(str(request.query_params["toDate"])),
            }
            # Used to validate the `from_date` and `to_date`.
            serializer = AssignReservationSerializer(data=request_data)  # type: ignore
            if serializer.is_valid():
                pls = ParkingLot.objects.is_available(
                    int(garage_pk),
                    serializer.validated_data["from_date"],  # type: ignore
                    serializer.validated_data["to_date"],  # type: ignore
                )
                serializer = ParkingLotSerializer(pls, many=True)  # type: ignore
                return BackendResponse(serializer.data, status=status.HTTP_200_OK)
            return BackendResponse(
                [serializer.errors], status=status.HTTP_400_BAD_REQUEST  # type: ignore
            )
        except KeyError:
            serializer = ParkingLotSerializer(
                ParkingLot.objects.filter(garage_id=garage_pk), many=True
            )
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)


class ParkingLotAssignView(_OriginAPIView):
    """
    View class to assign a random free parking lot for making a reservation.
    """

    origins = ["web", "app"]
    http_method_names = ["get"]

    def get(self, request: Request, garage_pk: int, format=None) -> BackendResponse:
        if (resp := _OriginAPIView.get(self, request, format)) is not None:
            return resp
        request_data = {
            "from_date": str(request.query_params["fromDate"]).replace(" ", "+"),
            "to_date": str(request.query_params["toDate"]).replace(" ", "+"),
        }
        assignment_serializer = AssignReservationSerializer(data=request_data)  # type: ignore
        if assignment_serializer.is_valid():
            valid_data: dict[str, Any] = assignment_serializer.validated_data  # type: ignore
            pls = list(
                filter(
                    lambda pl: not pl.booked,
                    ParkingLot.objects.is_available(
                        int(garage_pk),
                        valid_data["from_date"],
                        valid_data["to_date"],
                    ),
                )
            )
            pl = pls[randint(0, len(pls))]
            serializer = ParkingLotSerializer(pl)
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            assignment_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class ParkingLotRPiView(_OriginAPIView):
    """
    View class for handling request coming from the Raspberry Pi. The request only contains the garage id and parking lot number.
    """

    permission_classes = [AllowAny]
    origins = ["rpi"]
    http_method_names = ["put"]

    def put(self, request: Request, format=None) -> Response:
        if (resp := super().put(request, format)) is not None:
            return resp
        data = parse_frontend_json(request)
        serializer = RPIParkingLotSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            parking_lot = ParkingLot.objects.filter(
                garage_id=serializer.validated_data["garage_id"],  # type: ignore
                parking_lot_no=serializer.validated_data["parking_lot_no"],  # type: ignore
            )
            
            if len(parking_lot) == 1:
                parking_lot.update(occupied=serializer.validated_data["occupied"])  # type: ignore
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
