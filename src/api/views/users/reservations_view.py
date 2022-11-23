from datetime import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.core.views import (
    BaseAPIView,
    BackendResponse,
    _dict_key_to_case,
    _OriginAPIView,
)
from src.core.utils import to_snake_case
from src.api.models import Reservation, ParkingLot
from src.api.serializers import GetReservationSerializer, PostReservationSerializer


class ReservationsView(BaseAPIView):
    """
    A view class to get all reservations from the currently logged in user and to post new one.
    """

    origins = ["app", "web"]
    serializer = {"get": GetReservationSerializer}
    get_user_id = True
    model = Reservation

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := _OriginAPIView.post(self, request, format)) is not None:
            return resp
        data = _dict_key_to_case(JSONParser().parse(request), to_snake_case)
        serializer = PostReservationSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            serializer.save(user=request.user)
            if not ReservationsView.parking_lot_is_available(
                serializer.validated_data["parking_lot_id"],  # type:ignore
                serializer.validated_data["from_date"],  # type:ignore
                serializer.validated_data["to_date"],  # type:ignore
            ):
                return BackendResponse(
                    [
                        "The parking lot is already occupied on that day and time, please choose another one."
                    ],
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return BackendResponse(serializer.data, status=status.HTTP_201_CREATED)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def parking_lot_is_available(
        pk: int, start_time: datetime, end_time: datetime
    ) -> bool:
        pl_reservations = Reservation.objects.filter(parking_lot_id=pk)
        print(pl_reservations)
        return (
            True
            if not pl_reservations
            else not any(
                map(
                    lambda reservation: ReservationsView.in_daterange(
                        reservation.from_date, reservation.to_date, start_time, end_time
                    ),
                    pl_reservations,
                )
            )
        )

    @staticmethod
    def in_daterange(
        st1: datetime, et1: datetime, st2: datetime, et2: datetime
    ) -> bool:
        return (
            st1 <= st2 <= et1
            or st1 <= et2 <= et1
            or st2 <= st1 <= et2
            or st1 <= et2 <= et1
        )
