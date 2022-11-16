from rest_framework import status
from rest_framework.request import Request

from src.core.views import BackendResponse
from src.core.utils import OriginAPIView
from src.api.models import Reservations
from src.api.serializers import GetReservationsSerializer


class ReservationsView(OriginAPIView):
    """
    A view class to get all the parking lots.
    """

    origins = ["app", "web"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        user_reservations = Reservations.objects.filter(user_id=request.user.pk)
        serializer = GetReservationsSerializer(user_reservations, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
