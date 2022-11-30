import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.api.models.garages.price import Price
from src.api.serializers.payment.checkout_serializer import CheckoutSessionSerializer
from src.core.views import BackendResponse, _OriginAPIView

from django.utils import timezone


def _get_prices_to_pay(licence_plate: LicencePlate):
    # Fetch garage prices from database
    prices = Price.objects.filter(garage=licence_plate.garage)
    prices = sorted(prices, key=lambda p: p.duration, reverse=True)

    if len(prices) == 0:
        return []

    # Get time the user has to pay for
    updated_at = licence_plate.updated_at
    time_to_pay = (timezone.now() - updated_at)

    # Go over each and reduce te time to pay by the largest possible amount
    preview_items = []
    for price in prices:

        item = {
            # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
            'price': price,
            'quantity': 0,
        }

        if price.duration >= datetime.timedelta(0):  # Make sure the loop completes
            while time_to_pay > price.duration:
                time_to_pay -= price.duration
                item['quantity'] += 1

        if item['quantity'] > 0:
            preview_items.append(item)

    return preview_items


class CheckoutPreviewView(_OriginAPIView):
    """
    A view to create a payment session
    """

    permission_classes = [AllowAny]
    origins = ["web", "app"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        checkout_data = JSONParser().parse(request)
        checkout_serializer = CheckoutSessionSerializer(data=checkout_data)

        if checkout_serializer.is_valid():
            licence_plate = LicencePlate.objects.get(user=request.user,
                                                     licence_plate=checkout_serializer.validated_data['licence_plate'])
            print(_get_prices_to_pay(licence_plate))
            preview_items = [
                {
                    'price': price['price'].price,
                    'duration': price['price'].duration,
                    'price_string': price['price'].price_string,
                    'quantity': price['quantity'],
                }
                for price in _get_prices_to_pay(licence_plate)
            ]

            if len(preview_items) == 0:
                # No payment is needed
                return BackendResponse(["No payment required"], status=status.HTTP_200_OK)

            return BackendResponse({
                'items': preview_items,
            }, status=status.HTTP_200_OK)

        return BackendResponse(
            ["Invalid licence plate entered."],
            status=status.HTTP_400_BAD_REQUEST,
        )
