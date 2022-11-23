from src.api.models import ParkingLot
from src.api.serializers import ParkingLotSerializer
from src.core.views import PkAPIView
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


class RpiParkingLotView(PkAPIView):
    """
    A view class for handling request coming from the Raspberry Pi. The request only contains the garage id and parking lot number.
    """

    origins = ["rpi"]
