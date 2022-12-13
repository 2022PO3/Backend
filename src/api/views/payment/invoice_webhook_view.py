from os import getenv

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.views.payment.checkout_webhook_view import complete_order
from src.core.utils.payment_mails import send_payment_mail, PaymentResult
from src.core.views import BackendResponse

import stripe


class InvoiceWebhookView(APIView):
    """
    A view to listen for invoice updates from the stripe servers.
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
            BackendResponse(['Something went wrong communicating with Stripe.', str(e)],
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print(event['type'])

        if event['type'] == 'invoice.finalization_failed':
            # Retry?
            invoice = event['data']['object']

        if event['type'] == 'invoice.finalized':
            # Stripe is now trying to collect the money so the user can leave the garage
            invoice = event['data']['object']
            try:
                invoice.pay()
            except stripe.error.CardError:
                # Error gets handled by a 'invoice.payment_failed' event
                pass
            return complete_order(invoice.metadata)

        if event['type'] == 'invoice.payment_failed':
            # These events correspond to a failed automatic charge, we have to send an email with another payment option
            # to the user
            invoice = event['data']['object']
            send_payment_mail(PaymentResult.InvoiceFailed, invoice.metadata['user_id'], invoice_url=invoice.hosted_invoice_url)
            return BackendResponse(f"Automatic charge failed, sent email to user", status=status.HTTP_200_OK, )
        if event['type'] == 'invoice.payment_succeeded':
            # The payment succeeded and the user can be notified
            invoice = event['data']['object']
            send_payment_mail(PaymentResult.Succeeded, invoice.metadata['user_id'])
            return BackendResponse(f"Payment succeeded, sent email to user.", status=status.HTTP_200_OK, )

        return BackendResponse(f"Processed event {event['type']}", status=status.HTTP_200_OK, )
