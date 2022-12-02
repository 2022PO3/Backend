import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.api.models.garages.price import Price
from src.api.serializers import LicencePlateSerializer
from src.api.serializers.payment.checkout_serializer import CheckoutSessionSerializer
from src.api.views.payment.checkout_preview_view import _get_prices_to_pay
from src.core.views import BackendResponse, _OriginAPIView
from src.users.models import User

from django.shortcuts import redirect

from django.utils import timezone

import stripe

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
WEBSITE_URL = 'https://po3backend.ddns.net/app'


class CreateCheckoutSessionView(_OriginAPIView):
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

            line_items = [
                {
                    'price': price['price'].stripe_identifier,
                    'quantity': price['quantity'],
                }
                for price in _get_prices_to_pay(licence_plate)
            ]

            if len(line_items) == 0:
                # No payment is needed
                return BackendResponse(["No payment required"], status=status.HTTP_200_OK)

            try:
                # Maak betaalpagina
                checkout_session = stripe.checkout.Session.create(
                    line_items=line_items,
                    mode='payment',
                    success_url=WEBSITE_URL + '/checkout-session-succes',  # Add id to find payment intent and user
                    cancel_url=WEBSITE_URL + '/checkout-session-canceled',
                    metadata={
                        'user_id': request.user.pk,
                        'licence_plate': licence_plate.licence_plate
                    }
                )
            except Exception as e:
                return BackendResponse(
                    ['Failed to create payment session.', str(e)],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return BackendResponse({
                'url': checkout_session.url,
            }, status=status.HTTP_201_CREATED)

        return BackendResponse(
            ["Invalid licence plate entered."],
            status=status.HTTP_400_BAD_REQUEST,
        )
