from rest_framework.request import Request
from src.api.models.garages import Garages
from src.api.serializers.garages_serializer import GaragesSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser


@api_view(["GET"])
def get_garages(request: Request) -> Response:
    """
    List all code snippets, or create a new snippet.
    """
    garages = Garages.objects.all()
    serializer = GaragesSerializer(garages, many=True)
    return Response({"data": serializer.data}, status=200)


@api_view(["POST"])
def post_garage(request: Request) -> Response:
    """
    Create a new garage in the database.
    """
    garage_data = JSONParser().parse(request)
    garages_serializer = GaragesSerializer(data=garage_data)
    if garages_serializer.is_valid():
        garages_serializer.save()
        return Response({"data": garages_serializer.data}, status=201)
    return Response({"errors": garages_serializer.errors}, status=400)
