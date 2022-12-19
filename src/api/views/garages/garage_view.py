from src.core.exceptions import BackendException
from src.core.views import BackendResponse, PkAPIView, BaseAPIView, parse_frontend_json
from src.api.models import Garage, ParkingLot
from dateutil.parser import parse
from django.http import Http404

from src.api.serializers import (
    GarageSerializer,
    ParkingLotSerializer,
    AssignReservationSerializer,
)
from src.users.permissions import IsGarageOwner
from rest_framework.request import Request
from rest_framework import status


class GaragesDetailView(PkAPIView):
    """
    A view class which incorporates the views regarding single instance of the
    `Garage`-model, which makes it possible to query a single garage on `pk` and to update a
    garage on `pk`.
    """

    origins = ["app", "web", "rpi"]
    permission_classes = [IsGarageOwner]
    model = Garage
    serializer = GarageSerializer
    user_id = True
    http_method_names = ["get", "put", "delete"]


class GaragesListView(BaseAPIView):
    """
    A view class to get all the garages and to post a new garage.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    serializer = {"get": GarageSerializer, "post": GarageSerializer}
    model = Garage
    post_user_id = True
