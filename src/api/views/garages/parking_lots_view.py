from src.api.models import ParkingLot
from src.api.serializers import ParkingLotSerializer
from src.core.views import PkAPIView, BaseAPIView
from src.users.permissions import IsGarageOwner


class ParkingLotsListView(PkAPIView):
    """
    A view class which renders all the parking lots for a given garage with `pk`.
    """

    origins = ["app", "web"]
    column = "garage_id"
    model = ParkingLot
    serializer = ParkingLotSerializer
    list = True


class ParkingLotsDetailView(BaseAPIView):
    """
    A view class which renders a PUT-request for a parking lot with the given `pk`.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    model = ParkingLot
    serializer = ParkingLotSerializer
