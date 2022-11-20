from django.http import Http404

from rest_framework import status
from rest_framework.request import Request

from src.core.views import BackendResponse, GetObjectMixin, _OriginAPIView
from src.api.models import Price
from src.api.serializers import PriceSerializer


class PricesView(_OriginAPIView, GetObjectMixin):
    """
    A view class which renders all the prices for a given garage with `pk`.
    """

    origins = ["app", "web"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            garage_prices = Price.objects.filter(garage_id=pk)
        except Http404:
            return BackendResponse(
                [f"The corresponding garage with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PriceSerializer(garage_prices, many=True)
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)
