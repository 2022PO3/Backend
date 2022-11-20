from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.api.models import OpeningHour
from src.api.serializers import OpeningHourSerializer
from src.core.views import BackendResponse, _OriginAPIView, PkAPIView, BaseAPIView
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
    """
    
    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp

        opening_hour = JSONParser().parse(request)
        opening_hours_serializer = OpeningHourSerializer(data=opening_hour)
        if opening_hours_serializer.is_valid():
            opening_hours = opening_hours_serializer.save()
            self.check_object_permissions(request, opening_hours)
            return BackendResponse(
                opening_hours_serializer.data, status=status.HTTP_201_CREATED
            )
        return BackendResponse(
            opening_hours_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
"""
