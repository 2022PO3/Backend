from src.api.models import Garage, GarageSettings
from src.api.serializers import GarageSettingsSerializer
from src.core.views import PkAPIView
from src.users.permissions import IsGarageOwner


class PkGarageSettingsView(PkAPIView):
    """
    A view class which renders the settings for a given garage with `pk`. These include all fields from the `GarageSettings`-model, as well as the location.
    """

    origins = ["app", "web"]
    fk_model = Garage
    serializer = GarageSettingsSerializer
    model = GarageSettings
    permission_classes = [IsGarageOwner]
    http_method_names = ["get", "put", "delete"]
