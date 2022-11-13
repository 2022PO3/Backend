from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from src.core.views import BackendResponse, GetObjectMixin
from src.api.models import LicencePlates
from src.api.serializers import LicencePlatesSerializer



class LicencePlateList(APIView):
    """
    A view class to get all the licence plates.
    """

    def get(self, request: Request, format=None) -> BackendResponse:
        licence_plates = LicencePlates.objects.all()
        serializer = LicencePlatesSerializer(licence_plates, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None) -> BackendResponse:
        licence_plate_data = JSONParser().parse(request)
        licence_plate_serializer = PostLicencePlateSerializer(data=licence_plate_data)
        if licence_plate_serializer.is_valid():
        LicencePlates.handle_licence_plate(
                licence_plate_serializer.data,
            )
            return BackendResponse(
                licence_plate_serializer.data, status=status.HTTP_201_CREATED
            
            )
        return BackendResponse(
            licence_plate_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
        
class LicencePlateDetail(APIView, GetObjectMixin):
    """
    Update a `LicencePlate` with the given `pk`.
    """

    def put(self, request: Request, pk: int, format=None) -> BackendResponse:
        licence_plate_data = JSONParser().parse(request)
        try:
            licence_plate = self.get_object(LicencePlates, pk)
        except Http404:
            return BackendResponse(
                [f"The given licence plate with id {pk} does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LicencePlatesSerializer(licence_plate, data=licence_plate_data)
        if serializer.is_valid():
            serializer.save()
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
