from src.api.models import LicencePlate
from src.api.serializers import LicencePlateSerializer, PostLicencePlateSerializer
from src.core.views import PkAPIView, BaseAPIView


class LicencePlateListView(BaseAPIView):
    """
    Returns a list of the licence plates belonging to a user.
    """

    origins = ["app", "web"]
    serializer = {"get": LicencePlateSerializer, "post": LicencePlateSerializer}
    model = LicencePlate
    get_user_id = True
    post_user_id = True


class LicencePlateDetailView(PkAPIView):
    """
    Update a `LicencePlate` with the given `pk`.
    """

    origins = ["app", "web"]
    model = LicencePlate
    serializer = PostLicencePlateSerializer
    user_id = True
