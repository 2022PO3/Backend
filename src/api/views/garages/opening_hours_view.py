from rest_framework.request import Request

from src.api.models import OpeningHour
from src.api.serializers import OpeningHourSerializer
from src.core.views import BackendResponse, PkAPIView
from src.users.permissions import IsGarageOwner


class OpeningHoursDetailView(PkAPIView):
    """
    View class which handles GET-, PUT- and DELETE-requests for opening hours with `pk`.
    Getting, updating and deleting is only allowed for garage owners.
    """

    origins = ["app", "web"]
    serializer = OpeningHourSerializer
    model = OpeningHour
    permission_classes = [IsGarageOwner]
    http_method_names = ["get", "put", "delete"]


class OpeningHoursGarageView(PkAPIView):
    """
    View class which handles GET- and POST-requests for opening hours of garage garage with
    `garage_pk`.
    Posting is only allowed by garage owners.
    """

    origins = ["app", "web"]
    column = "garage_id"
    serializer = OpeningHourSerializer
    model = OpeningHour
    permission_classes = [IsGarageOwner]
    return_list = True
    http_method_names = ["get", "post"]

    def get(self, request: Request, garage_pk: int, format=None) -> BackendResponse:
        return super().get(request, garage_pk, format)
