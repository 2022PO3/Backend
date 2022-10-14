from django.http import HttpResponse, JsonResponse
from src.api.models.garages import Garage
from src.api.serializers.garages_serializer import GarageSerializer


def garages(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        garages = Garage.objects.all()
        serializer = GarageSerializer(garages, many=True)
        return JsonResponse(serializer.data, safe=False)
    return HttpResponse(400)
