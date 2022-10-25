from rest_framework.request import Request
from rest_framework import status
from src.api.models.garages import Garages
from src.api.serializers.garages_serializer import GaragesSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser


@api_view(["GET", "POST"])
def get_garages(request: Request) -> Response:
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        garages = Garages.objects.all()
        serializer = GaragesSerializer(garages, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    elif request.method == "POST":
        print(request)
        print(request.data)
        garage_data = JSONParser().parse(request)
        garages_serializer = GaragesSerializer(data=garage_data)
        if garages_serializer.is_valid():
            garages_serializer.save()
            return Response(
                {"data": garages_serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"errors": garages_serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
