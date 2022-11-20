from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.core.views import BackendResponse, _OriginAPIView, BaseAPIView
from src.api.models import Reservation
from src.api.serializers import PostReservationSerializer


class ReservationsView(BaseAPIView):
    """
    A view class to get all reservations from the currently logged in user.
    """

    origins = ["app", "web"]
    serializer = PostReservationSerializer
    user_id = True
    model = Reservation

    """
    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        user_reservations = Reservations.objects.filter(user_id=request.user.pk)
        serializer = ReservationsSerializer(user_reservations, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
    """
    """
    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        reservation = JSONParser().parse(request)
        reservation_serializer = ReservationsSerializer(data=reservation)
        if reservation_serializer.is_valid():
            reservation_serializer.save(user=request.user)
            return BackendResponse(
                reservation_serializer.data, status=status.HTTP_201_CREATED
            )
        return BackendResponse(
            reservation_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    """
