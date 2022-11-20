from src.core.views import PkAPIView, BaseAPIView
from src.api.models import Garage
from src.api.serializers import GarageSerializer
from src.users.permissions import IsGarageOwner


class GarageDetailView(PkAPIView):
    """
    A view class which incorporates the views regarding single instance of the
    `Garage`-model, which makes it possible to query a single garage on `pk`.
    """

    origins = ["app", "web"]
    model = Garage
    serializer = GarageSerializer


class GarageListView(BaseAPIView):
    """
    A view class to get all the garages and to post a new garage.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    serializer = GarageSerializer
    model = Garage
    post_user_id = True
