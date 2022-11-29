from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.api.models.garages.price import Price
from src.api.serializers.payment.checkout_serializer import CheckoutSessionSerializer
from src.core.views import BackendResponse, _OriginAPIView
from src.users.models import User

from django.shortcuts import redirect

from datetime import datetime

import stripe

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
stripe.api_key = 'sk_test_51Lf1SsGRh96C3wQGfjc1BuPw2AhNPQpteJ0fz3JXRiD8QzpOb5nVKeNDSOKyLpfw6qcVUZ9936duVmrylnAqWf1t00kkRqidz1'
endpoint_secret = ''


def create_line_items(user: User, licence_plate: LicencePlate):
    # Fetch garage prices from database
    prices = Price.objects.get(garage=licence_plate.garage)
    prices = sorted(prices, key=lambda p: p.duration, reverse=True)

    if len(prices) == 0:
        return []

    # Get time the user has to pay for
    updated_at = licence_plate.updated_at
    time_to_pay = datetime.now() - updated_at

    # Go over each and reduce te time to pay by the largest possible amount
    line_items = []
    for price in prices:
        item = {
            # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
            'price': price.stripe_identifier,
            'quantity': 0
        }
        while time_to_pay > price.amount:
            time_to_pay -= price.duration
            item['quantity'] += 1

        if item['quantity'] > 0:
            line_items.append(item)

    return line_items


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

            line_items = create_line_items(user=request.user, licence_plate=licence_plate)

            WEBSITE_URL = 'https://po3backend.ddns.net/app'

            try:
                # Maak betaalpagina
                checkout_session = stripe.checkout.Session.create(
                    line_items=line_items,
                    mode='payment',
                    success_url=WEBSITE_URL + '/checkout-session-succes',  # Add id to find payment intent and user
                    cancel_url=WEBSITE_URL + '/checkout-session-canceled',
                )
            except Exception as e:
                return BackendResponse(
                    ['Failed to create payment session.'],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return redirect(checkout_session.url)

        return BackendResponse(
            ["Invalid licence plate entered."],
            status=status.HTTP_400_BAD_REQUEST,
        )
