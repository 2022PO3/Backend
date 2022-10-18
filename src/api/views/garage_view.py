from django.http import HttpResponse, JsonResponse
from src.api.models.garages import Garages
from src.api.serializers.garages_serializer import GaragesSerializer


def garages(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        garages = Garages.objects.all()
        serializer = GaragesSerializer(garages, many=True)
        return JsonResponse(serializer.data, safe=False)
    return HttpResponse(400)
