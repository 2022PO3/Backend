from os import getenv

from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.core.views import BackendResponse
from src.users.models import User


import stripe

def complete_order(session: stripe.checkout.Session) -> BackendResponse:
    metadata = session.metadata
    if 'licence_plate' in metadata.keys() and 'user_id' in metadata.keys():
        licence_plate = session.metadata['licence_plate']
        user_id = session.metadata['user_id']
    else:
        return BackendResponse(['The required data to complete the order was not included in the session metadata.'],
                               status=status.HTTP_400_BAD_REQUEST)

    licence_plate: LicencePlate = LicencePlate.objects.get(user=User.objects.get(pk=user_id),
                                                           licence_plate=licence_plate)

    licence_plate.updated_at = timezone.now()

    licence_plate.save()
    return BackendResponse('Completed order', status=status.HTTP_200_OK)



class CheckoutWebhookView(APIView):
    """
    A view to listen for checkout updates from the stripe servers.
    """

    permission_classes = [AllowAny]  # The post request checks if the request comes from Stripe

    def post(self, request: Request, format=None) -> BackendResponse:

        if 'STRIPE_SIGNATURE' not in request.headers:
            return BackendResponse(['This endpoint is only accessible by Stripe.'], status=status.HTTP_403_FORBIDDEN)

        sig_header = request.headers['STRIPE_SIGNATURE']
        payload = request.body

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, getenv('STRIPE_CHECKOUT_WEBHOOK_KEY')
            )
        except ValueError as e:
            # Invalid payload
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            print(str(e))
            BackendResponse(['Something went wrong communicating with Stripe.', str(e)], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Fulfill the purchase...
            complete_order(session)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            # Save an order in your database, marked as 'awaiting payment'
            # create_order(session)

            # Check if the order is already paid (for example, from a card payment)
            #
            # A delayed notification payment will have an `unpaid` status, as
            # you're still waiting for funds to be transferred from the customer's
            # account.
            if session.payment_status == "paid":
                # Fulfill the purchase
                complete_order(session)

        elif event['type'] == 'checkout.session.async_payment_succeeded':
            session = event['data']['object']

            # Fulfill the purchase
            complete_order(session)

        elif event['type'] == 'checkout.session.async_payment_failed':
            session = event['data']['object']

        # Passed signature verification
        return BackendResponse("Order is fulfilled.", status=status.HTTP_200_OK, )
