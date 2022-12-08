import datetime
from django.utils import timezone

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.api.models import Price
from src.api.serializers import CheckoutSessionSerializer
from src.core.views import BackendResponse, _OriginAPIView


def _get_prices_to_pay(licence_plate: LicencePlate):
    # Fetch garage prices from database
    prices = Price.objects.filter(garage=licence_plate.garage)
    prices = sorted(prices, key=lambda p: p.duration, reverse=True)

    if len(prices) == 0:
        return []

    # Get time the user has to pay for
    updated_at = licence_plate.updated_at
    time_to_pay = timezone.now() - updated_at

    # Go over each and reduce te time to pay by the largest possible amount
    preview_items = []
    for price in prices:

        item = {
            # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
            "price": price,
            "quantity": 0,
        }
        if price.duration >= datetime.timedelta(0):  # Make sure the loop completes
            while time_to_pay > price.duration:
                time_to_pay -= price.duration
                item["quantity"] += 1

        if item["quantity"] > 0:
            preview_items.append(item)

    # Calculate time in which app has to refresh
    refresh_time = prices[-1].duration - time_to_pay

    return preview_items, refresh_time


class CheckoutPreviewView(_OriginAPIView):
    """
    A view to create a payment session
    """

    permission_classes = [AllowAny]
    origins = ["web", "app"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        checkout_data = {"licence_plate": request.query_params["licence_plate"]}
        checkout_serializer = CheckoutSessionSerializer(data=checkout_data)  # type: ignore

        if checkout_serializer.is_valid():
            try:
                licence_plate = LicencePlate.objects.get(
                    user=request.user,
                    licence_plate=checkout_serializer.validated_data["licence_plate"],  # type: ignore
                )
            except:
                return BackendResponse(
                    ["Licence plate does not exist for this user."],
                    status=status.HTTP_400_BAD_REQUEST,
                )

            items, refresh_time = _get_prices_to_pay(licence_plate)

            preview_items = [
                {
                    "id": item["price"].pk,
                    "garage_id": item["price"].garage_id,
                    "price": item["price"].price,
                    "valuta": item["price"].valuta,
                    "duration": str(item["price"].duration),
                    "price_string": item["price"].price_string,
                    "quantity": item["quantity"],
                }
                for item in items
            ]

            if len(preview_items) == 0:
                # No payment is needed
                return BackendResponse(
                    ["No payment required"], status=status.HTTP_200_OK
                )

            return BackendResponse(
                {
                    "items": preview_items,
                    "refresh_time": int(refresh_time.total_seconds()),
                },
                status=status.HTTP_200_OK,
            )

        return BackendResponse(
            ["Invalid licence plate entered."],
            status=status.HTTP_400_BAD_REQUEST,
        )
