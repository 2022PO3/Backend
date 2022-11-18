from django.http import Http404

from rest_framework import status
from rest_framework.request import Request

from src.core.views import BackendResponse, GetObjectMixin
from src.core.utils import OriginAPIView
from src.api.models import Prices
from src.api.serializers import PricesSerializer


class PricesView(OriginAPIView, GetObjectMixin):
    """
    A view class which renders all the prices for a given garage with `pk`.
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
        serializer = PricesSerializer(garage_prices, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
