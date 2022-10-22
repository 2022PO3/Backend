from urllib.request import Request
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response

from src.api.models.parking_lots import ParkingLots
from src.api.serializers.parking_lots_serializer import ParkingLotsSerializer
from rest_framework.decorators import api_view


@api_view(["GET"])
def get_parking_lots(request: Request) -> Response:
    """
    List all code snippets, or create a new snippet.
    """
    parking_lots = ParkingLots.objects.all()
    serializer = ParkingLotsSerializer(parking_lots, many=True)
    return Response({"data": serializer.data}, status=200)
