from src.api.models import LicencePlate
from src.api.serializers import LicencePlateSerializer, PostLicencePlateSerializer
from src.core.views import PkAPIView, BaseAPIView


class LicencePlateListView(BaseAPIView):
    """
    View class to get all the user's licence plates and to post new one.
    """

    origins = ["app", "web"]
    serializer = {"get": LicencePlateSerializer, "post": LicencePlateSerializer}
    model = LicencePlate
    get_user_id = True
    post_user_id = True


class PkLicencePlateView(PkAPIView):
    """
    View class to delete or update a `LicencePlate` with the given `pk`.
    """

    origins = ["app", "web"]
    model = LicencePlate
    serializer = PostLicencePlateSerializer
    user_id = True
