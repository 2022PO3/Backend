from src.api.models import OpeningHour
from src.api.serializers import OpeningHourSerializer
from src.core.views import PkAPIView, BaseAPIView
from src.users.permissions import IsGarageOwner


class PkOpeningHoursView(PkAPIView):
    """
    View class which renders all the opening hours for a given garage with `pk`.
    Deletion and updating is only allowed for garage owners.
    """

    origins = ["app", "web"]
    column = "garage_id"
    serializer = OpeningHourSerializer
    model = OpeningHour
    permission_classes = [IsGarageOwner]
    return_list = True
    http_method_names = ["get", "put", "delete"]


class PostOpeningHoursView(BaseAPIView):
    """
    View class which to add new opening hours to a garage.
    Only allowed for garage owners.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    model = OpeningHour
    serializer = {"post": OpeningHourSerializer}
