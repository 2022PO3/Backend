from os import getenv

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.core.views import BackendResponse


import stripe

class InvoiceWebhookView(APIView):
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
                payload, sig_header, getenv('STRIPE_INVOICE_WEBHOOK_KEY')
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


# Handle the event
        if event['type'] == 'invoice.created':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.deleted':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.finalization_failed':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.finalized':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.marked_uncollectible':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.paid':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.payment_action_required':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.sent':
            invoice = event['data']['object']
        elif event['type'] == 'invoice.voided':
            invoice = event['data']['object']
        # ... handle other event types
        else:
            print('Unhandled event type {}'.format(event['type']))

        print(invoice)

        # Passed signature verification
        return BackendResponse("Order is fulfilled.", status=status.HTTP_200_OK, )
