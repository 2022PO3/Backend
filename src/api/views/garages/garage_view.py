from rest_framework.permissions import AllowAny

from src.core.views import PkAPIView, BaseAPIView
from src.api.models import Garage

from src.api.serializers import GarageSerializer
from src.users.permissions import IsGarageOwner


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


class GarageRPiView(PkAPIView):
    origins = ["app", "web", "rpi"]
    permission_classes = [AllowAny]
    model = Garage
    serializer = GarageSerializer
    user_id = True
    http_method_names = ["get"]
