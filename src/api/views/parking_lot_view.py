from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from src.core.views import BackendResponse
from src.api.models import ParkingLots
from src.api.serializers import ParkingLotsSerializer


class ParkingLotList(APIView):
    """
    A view class to get all the parking lots.
    An authentication header is needed.
    """

    def get(self, request: Request, format=None) -> BackendResponse:
        parking_lots = ParkingLots.objects.all()
        serializer = ParkingLotsSerializer(parking_lots, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
