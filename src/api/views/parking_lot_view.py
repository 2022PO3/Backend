from urllib.request import Request
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView


from src.api.models.parking_lots import ParkingLots
from src.api.serializers.parking_lots_serializer import ParkingLotsSerializer
from rest_framework.decorators import api_view


class ParkingLotList(APIView):
    """
    A view class to get all the parking lots.
    """

    def get(self, request: Request, format=None) -> Response:
        parking_lots = ParkingLots.objects.all()
        serializer = ParkingLotsSerializer(parking_lots, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
