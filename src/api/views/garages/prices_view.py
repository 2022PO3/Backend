from django.http import Http404

from rest_framework import status
from rest_framework.request import Request

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import Prices
from src.api.serializers import GetPricesSerializer


class PricesView(OriginAPIView, GetObjectMixin):
    """
    A view class which renders the settings for a given garage. These include all fields from the `GarageSettings`-model, as well as the location and opening hours of the Garage. See the API-documentation for more details.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            garage_prices = Prices.objects.filter(garage_id=pk)
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = GetPricesSerializer(garage_prices, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
