from dateutil.parser import parse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser, ParseError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from src.api.models import ParkingLot
from src.api.serializers import ParkingLotSerializer, RPIParkingLotSerializer
from src.api.serializers import AssignReservationSerializer
from src.core.utils import to_snake_case
from src.core.views import PkAPIView, _OriginAPIView, _dict_key_to_case, BackendResponse
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

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := _OriginAPIView.get(self, request, format)) is not None:
            return resp
        try:
            request_data = {
                "from_date": parse(str(request.query_params["fromDate"])),
                "to_date": parse(str(request.query_params["toDate"])),
            }
            serializer = AssignReservationSerializer(data=request_data)  # type: ignore
            if serializer.is_valid():
                pls = ParkingLot.objects.is_available(
                    int(pk),
                    serializer.validated_data["from_date"],  # type: ignore
                    serializer.validated_data["to_date"],  # type: ignore
                )
                serializer = ParkingLotSerializer(pls, many=True)  # type: ignore
                return BackendResponse(serializer.data, status=status.HTTP_200_OK)
            return BackendResponse(
                [serializer.errors], status=status.HTTP_400_BAD_REQUEST  # type: ignore
            )
        except KeyError:
            serializer = ParkingLotSerializer(
                ParkingLot.objects.filter(garage_id=pk), many=True
            )
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)


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
                parking_lot.update(occupied=serializer.validated_data["occupied"])  # type: ignore
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
