import stripe

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from src.api.models import LicencePlate
from src.api.serializers import CheckoutSessionSerializer
from src.core.views import BackendResponse, _OriginAPIView

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
WEBSITE_URL = "https://po3backend.ddns.net/app"


class SendInvoiceView(_OriginAPIView):
    """
    A view to send an invoice for a certain licence plate. Used for testing only because real
    invoices will be sent through the licence_plate_image_view.
    """

    origins = ["web", "app"]
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        checkout_data = JSONParser().parse(request)
        checkout_serializer = CheckoutSessionSerializer(data=checkout_data)  # type: ignore

        if checkout_serializer.is_valid():
            try:
                licence_plate = LicencePlate.objects.get(
                    user=request.user,
                    licence_plate=checkout_serializer.validated_data["licence_plate"],  # type: ignore
                )
            except LicencePlate.DoesNotExist:
                return BackendResponse(
                    ["Licence plate does not exist for this user."],
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                request.user.send_invoice(licence_plate)
            except stripe.error.InvalidRequestError as e:  # type: ignore
                return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as e:  # type: ignore
                return BackendResponse(
                    ["Something went wrong communicating with Stripe.", str(e)],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return BackendResponse("Sent Invoice.", status=status.HTTP_200_OK)

        return BackendResponse(
            ["Invalid licence plate entered."],
            status=status.HTTP_400_BAD_REQUEST,
        )
