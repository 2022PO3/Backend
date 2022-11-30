from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny

from src.core.views import BackendResponse, _OriginAPIView
from src.users.models import User
from src.api.serializers import LoginSerializer, UsersSerializer

from src.core.views import _OriginAPIView

import stripe

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
stripe.api_key = 'sk_test_51Lf1SsGRh96C3wQGfjc1BuPw2AhNPQpteJ0fz3JXRiD8QzpOb5nVKeNDSOKyLpfw6qcVUZ9936duVmrylnAqWf1t00kkRqidz1'
endpoint_secret = 'whsec_cbc3c8904ec1b2bcd029776f6217f81b9d11da0c4c06b472b574b529c6cf220c'


def email_customer_about_failed_payment(session):
    pass


def fulfill_order(session):
    pass


def create_order(session):
    pass


class CheckoutWebhookView(APIView):
    """
    A view to listen for checkout updates from the stripe servers.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, format=None) -> BackendResponse:

        if 'STRIPE_SIGNATURE' not in request.headers:
            return BackendResponse(['This endpoint is only accessible by Stripe.'], status=status.HTTP_403_FORBIDDEN)

        sig_header = request.headers['STRIPE_SIGNATURE']
        payload = request.body

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Fulfill the purchase...
            fulfill_order(session)
        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Save an order in your database, marked as 'awaiting payment'
            create_order(session)

            # Check if the order is already paid (for example, from a card payment)
            #
            # A delayed notification payment will have an `unpaid` status, as
            # you're still waiting for funds to be transferred from the customer's
            # account.
            if session.payment_status == "paid":
                # Fulfill the purchase
                fulfill_order(session)

        elif event['type'] == 'checkout.session.async_payment_succeeded':
            session = event['data']['object']

            # Fulfill the purchase
            fulfill_order(session)

        elif event['type'] == 'checkout.session.async_payment_failed':
            session = event['data']['object']

            # Send an email to the customer asking them to retry their order
            email_customer_about_failed_payment(session)

        # Passed signature verification
        return BackendResponse(["Order is fulfilled."], status=status.HTTP_200_OK, )
