from os import getenv

from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.views.payment.checkout_webhook_view import complete_order
from src.core.settings import EMAIL_HOST_USER
from src.core.views import BackendResponse

import stripe

from src.users.models import User


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
            BackendResponse(['Something went wrong communicating with Stripe.', str(e)],
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if event['type'] == 'invoice.finalization_failed':
            # Retry?
            invoice = event['data']['object']

        if event['type'] == 'invoice.finalized':
            # Stripe is now trying to collect the money so the user can leave the garage
            invoice = event['data']['object']
            return complete_order(invoice.metadata)

        if event['type'] in ['invoice.marked_uncollectible', 'invoice.payment_action_required',
                             'invoice.payment_failed', 'invoice.voided']:
            # These events correspond to a failed automatic charge, we have to send an email with another payment option
            # to the user
            invoice = event['data']['object']
            send_invoice_mail(False, invoice)
            return BackendResponse(f"Automatic charge failed, sent email to user", status=status.HTTP_200_OK, )
        if event['type'] == 'invoice.payment_succeeded':
            # The payment succeeded and the user can be notified
            invoice = event['data']['object']
            send_invoice_mail(True, invoice)
            return BackendResponse(f"Payment succeeded, sent email to user.", status=status.HTTP_200_OK, )

        print(event['type'])

        return BackendResponse(f"Processed event {event['type']}", status=status.HTTP_200_OK, )


def send_invoice_mail(succeeded: True, invoice: stripe.Invoice):
    user = User.objects.get(pk=invoice.metadata['user_id'])

    if succeeded:
        msg_plain = render_to_string("payment_succeeded_template.txt", {})
        msg_html = render_to_string("payment_succeeded_template.html", {})
    else:

        msg_plain = render_to_string(
            "invoice_failed_template.txt", {"checkout_url": invoice.hosted_invoice_url}
        )
        msg_html = render_to_string(
            "invoice_failed_template.html", {"checkout_url": invoice.hosted_invoice_url}
        )
    send_mail(
        f"Parking boys payment {'succeeded' if succeeded else 'failed'}",
        msg_plain,
        EMAIL_HOST_USER,
        [user.email],
        html_message=msg_html,
    )
