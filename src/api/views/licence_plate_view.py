from rest_framework.request import Request
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from src.api.models.licence_plates import LicencePlates
from src.api.serializers.licence_plates_serializer import LicencePlatesSerializer


class LicencePlateList(APIView):
    """
    A view class to get all the licence plates.
    """

    def get(self, request: Request, format=None) -> Response:
        licence_plates = LicencePlates.objects.all()
        serializer = LicencePlatesSerializer(licence_plates, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None) -> Response:
        licence_plate_data = JSONParser().parse(request)
        licence_plate_serializer = LicencePlatesSerializer(data=licence_plate_data)
        if licence_plate_serializer.is_valid():
            licence_plate_serializer.save()
            return Response(
                {"data": licence_plate_serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"errors": licence_plate_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
