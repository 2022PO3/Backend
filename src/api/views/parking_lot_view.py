from django.http import HttpResponse, JsonResponse
from src.api.models.parking_lots import ParkingLots
from src.api.serializers.parking_lots_serializer import ParkingLotsSerializer


def parking_lots(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        parking_lots = ParkingLots.objects.all()
        serializer = ParkingLotsSerializer(parking_lots, many=True)
        return JsonResponse(serializer.data, safe=False)
    return HttpResponse(400)
