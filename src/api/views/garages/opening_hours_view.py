from src.api.models import OpeningHour
from src.api.serializers import OpeningHourSerializer
from src.core.views import PkAPIView, BaseAPIView
from src.users.permissions import IsGarageOwner


class GetOpeningHoursView(PkAPIView):
    """
    A view class which renders all the opening hours for a given garage with `pk`.
    """

    origins = ["app", "web"]
    column = "garage_id"
    serializer = OpeningHourSerializer
    model = OpeningHour
    list = True


class PostOpeningHoursView(BaseAPIView):
    """
    A view class which to add new opening hours to a garage.
    """

    origins = ["app", "web"]
    permission_classes = [IsGarageOwner]
    model = OpeningHour
    serializer = OpeningHourSerializer
