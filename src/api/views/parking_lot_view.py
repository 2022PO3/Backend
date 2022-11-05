from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from src.api.models import ParkingLots
from src.api.serializers import ParkingLotsSerializer


class ParkingLotList(APIView):
    """
    A view class to get all the parking lots.
    An authentication header is needed.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, format=None) -> Response:
        parking_lots = ParkingLots.objects.all()
        serializer = ParkingLotsSerializer(parking_lots, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
