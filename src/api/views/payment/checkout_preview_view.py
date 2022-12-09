import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.api.serializers.payment.checkout_serializer import CheckoutSessionSerializer
from src.core.utils.stripe_endpoints import send_invoice
from src.core.views import BackendResponse, _OriginAPIView


class CheckoutPreviewView(_OriginAPIView):
    """
    A view to create a payment session
    """

    permission_classes = [AllowAny]
    origins = ["web", "app"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        checkout_data = {'licence_plate': str(request.query_params['licence_plate'])}
        checkout_serializer = CheckoutSessionSerializer(data=checkout_data)

        if checkout_serializer.is_valid():
            try:
                licence_plate = LicencePlate.objects.get(user=request.user,
                                                         licence_plate=checkout_serializer.validated_data[
                                                             'licence_plate'])
            except LicencePlate.DoestNotExist:
                return BackendResponse(
                    ["Licence plate does not exist for this user."],
                    status=status.HTTP_404_NOT_FOUND,
                )

            items, refresh_time = licence_plate.get_prices_to_pay()

            send_invoice(request.user, licence_plate)

            preview_items = [
                {
                    'id': item['price'].pk,
                    'garage_id': item['price'].garage_id,
                    'price': item['price'].price,
                    'valuta': item['price'].valuta,
                    'duration': int(item['price'].duration.total_seconds()),
                    'price_string': item['price'].price_string,
                    'quantity': item['quantity'],
                }
                for item in items
            ]

            if len(preview_items) == 0:
                # No payment is needed
                return BackendResponse("No payment required", status=status.HTTP_200_OK)

            return BackendResponse({
                'items': preview_items,
                'refresh_time': int(refresh_time.total_seconds())
            }, status=status.HTTP_200_OK)

        return BackendResponse(
            ["Invalid licence plate entered."],
            status=status.HTTP_400_BAD_REQUEST,
        )
