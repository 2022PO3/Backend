from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from src.api.models import LicencePlates
from src.api.serializers import LicencePlatesSerializer


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


class LicencePlateDetail(APIView):
    """
    Update a `LicencePlate` with the given `pk`.
    """

    def get_object(self, pk: int) -> LicencePlates:
        """
        Retrieves the `LicencePlates`-object with the given `pk` from the database.
        """
        try:
            return LicencePlates.objects.get(pk=pk)
        except LicencePlates.DoesNotExist:
            raise Http404

    def put(self, request: Request, pk: int, format=None) -> Response:
        licence_plate_data = JSONParser().parse(request)
        try:
            licence_plate = self.get_object(pk)
        except Http404:
            return Response(
                {"errors": f"The given licence plate with id {pk} does not exist,"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LicencePlatesSerializer(licence_plate, data=licence_plate_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
