from rest_framework import status
from rest_framework.request import Request

from src.core.views import BackendResponse
from src.core.utils import OriginAPIView
from src.api.models import ParkingLots
from src.api.serializers import ParkingLotsSerializer


class ParkingLotListView(OriginAPIView):
    """
    A view class to get all the parking lots.
    """

    origins = ["app", "web"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        parking_lots = ParkingLots.objects.all()
        serializer = ParkingLotsSerializer(parking_lots, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
