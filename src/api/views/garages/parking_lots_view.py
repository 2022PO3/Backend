from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from src.api.models import ParkingLot
from src.api.serializers import ParkingLotSerializer, RPIParkingLotSerializer
from src.core.utils import to_snake_case
from src.core.views import PkAPIView, _OriginAPIView, _dict_key_to_case
from src.users.permissions import IsGarageOwner


class ParkingLotView(PkAPIView):
    """
    A view class which renders all the parking lots for a given garage with `pk`.
    """

    origins = ["app", "web"]
    column = "garage_id"
    permission_classes = [IsGarageOwner]
    model = ParkingLot
    serializer = ParkingLotSerializer
    list = True


class ParkingLotPutView(PkAPIView):
    """
    A view class which handles PUT-requests with the pk of the parking lot.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    model = ParkingLot
    serializer = ParkingLotSerializer


class RPiParkingLotView(_OriginAPIView):
    """
    A view class for handling request coming from the Raspberry Pi. The request only contains the garage id and parking lot number.
    """

    permission_classes = [AllowAny]
    origins = ["rpi"]

    def put(self, request: Request, format=None) -> Response:
        if (resp := super().put(request, format)) is not None:
            return resp
        data = _dict_key_to_case(JSONParser().parse(request), to_snake_case)
        serializer = RPIParkingLotSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            parking_lot = ParkingLot.objects.filter(
                garage_id=serializer.validated_data["garage_id"],  # type: ignore
                parking_lot_no=serializer.validated_data["parking_lot_no"],  # type: ignore
            )
            if len(parking_lot) == 1:
                parking_lot.update(occupied=not parking_lot[0].occupied)
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FreeParkingLotView(_OriginAPIView):
    pass
