from src.api.models import LicencePlate
from src.api.serializers import LicencePlateSerializer, LicencePlateRPiSerializer
from src.core.views import PkAPIView, BaseAPIView


class LicencePlateDetailView(PkAPIView):
    """
    View class to delete or update a `LicencePlate` with the given `pk`.
    """

    origins = ["app", "web"]
    model = LicencePlate
    serializer = LicencePlateRPiSerializer
    user_id = True


class LicencePlateListView(BaseAPIView):
    """
    View class to get all the user's licence plates and to post new one.
    """

    origins = ["app", "web"]
    serializer = {"get": LicencePlateSerializer, "post": LicencePlateSerializer}
    model = LicencePlate
    get_user_id = True
    post_user_id = True
