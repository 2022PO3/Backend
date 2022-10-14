from django.http import HttpResponse, JsonResponse
from src.api.models.parking_lots import ParkingLot
from src.api.serializers.parking_lots_serializer import ParkingLotSerializer


def parking_lots(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        parking_lots = ParkingLot.objects.all()
        serializer = ParkingLotSerializer(parking_lots, many=True)
        return JsonResponse(serializer.data, safe=False)
    return HttpResponse(400)
