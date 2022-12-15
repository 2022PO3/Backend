from src.core.views import PkAPIView, BaseAPIView
from src.api.models import Garage
from src.api.serializers import GarageSerializer
from src.users.permissions import IsGarageOwner


class PkGarageView(PkAPIView):
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


class ListGarageView(BaseAPIView):
    """
    A view class to get all the garages and to post a new garage.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    serializer = {"get": GarageSerializer}
    model = Garage
    post_user_id = True

class OwnedGarageListView(BaseAPIView):
    """
    A view class to get all the garages and to post a new garage.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    serializer = {"get": GarageSerializer}
    model = Garage
    get_user_id = True
    post_user_id = True
