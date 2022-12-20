import stripe

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from src.api.models import LicencePlate
from src.api.serializers import CheckoutSessionSerializer
from src.core.views import BackendResponse, _OriginAPIView


# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
WEBSITE_URL = "https://po3backend.ddns.net/web"


class CreateCheckoutSessionView(_OriginAPIView):
    """
    A view to create a payment session
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
            except LicencePlate.NotFoundError:  # type: ignore
                return BackendResponse(
                    ["Licence plate does not exist for this user."],
                    status=status.HTTP_404_NOT_FOUND,
                )
            items, _ = licence_plate.get_prices_to_pay()
            line_items = [
                {
                    "price": item["price"].stripe_identifier,  # type: ignore
                    "quantity": item["quantity"],
                }
                for item in items
            ]

            if not len(line_items):
                # No payment is needed
                return BackendResponse(
                    {"url": "No payment required"}, status=status.HTTP_200_OK
                )

            try:
                # Maak betaalpagina
                checkout_session = stripe.checkout.Session.create(
                    # customer=request.user.stripe_identifier,  # can be added to automatically fill in some details
                    # but the user won't be able to change their email
                    line_items=line_items,
                    mode="payment",
                    success_url=WEBSITE_URL + "/checkout/succes",
                    cancel_url=WEBSITE_URL + "/checkout/failed",
                    metadata={
                        "user_id": request.user.pk,
                        "licence_plate": licence_plate.licence_plate,
                    },
                )
            except Exception as e:
                return BackendResponse(
                    ["Failed to create payment session.", str(e)],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return BackendResponse(
                {
                    "url": checkout_session.url,
                },
                status=status.HTTP_201_CREATED,
            )

        return BackendResponse(
            ["Invalid licence plate entered."],
            status=status.HTTP_400_BAD_REQUEST,
        )
