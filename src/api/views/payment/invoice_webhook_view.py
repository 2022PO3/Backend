from os import getenv

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.views.payment.checkout_webhook_view import complete_payment
from src.core.utils.payment_mails import send_payment_mail, PaymentResult
from src.core.views import BackendResponse

import stripe


class InvoiceWebhookView(APIView):
    """
    View class to listen for invoice updates from the stripe servers.
    """

    # The post request checks if the request comes from Stripe
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if "STRIPE_SIGNATURE" not in request.headers:
            return BackendResponse(
                ["This endpoint is only accessible by Stripe."],
                status=status.HTTP_403_FORBIDDEN,
            )

        sig_header: str = request.headers["STRIPE_SIGNATURE"]
        payload = request.body

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, getenv("STRIPE_INVOICE_WEBHOOK_KEY")  # type: ignore
            )
        except ValueError as e:
            # Invalid payload
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:  # type: ignore
            # Invalid signature
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:  # type: ignore
            BackendResponse(
                ["Something went wrong communicating with Stripe.", str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if event["type"] == "invoice.finalization_failed":  # type: ignore
            # Retry?
            invoice = event["data"]["object"]  # type: ignore

        if event["type"] == "invoice.finalized":  # type: ignore
            # Stripe is now trying to collect the money so the user can leave the garage
            invoice = event["data"]["object"]  # type: ignore
            try:
                invoice.pay()
            except stripe.error.CardError:  # type: ignore
                # Error gets handled by a 'invoice.payment_failed' event
                pass
            return complete_payment(invoice.metadata)

        if event["type"] == "invoice.payment_failed":  # type: ignore
            # These events correspond to a failed automatic charge, we have to send an email with another payment option
            # to the user
            invoice = event["data"]["object"]  # type: ignore
            send_payment_mail(
                PaymentResult.InvoiceFailed,  # type: ignore
                invoice.metadata["user_id"],
                invoice_url=invoice.hosted_invoice_url,
            )  # type: ignore
            return BackendResponse(
                f"Automatic charge failed, sent email to user",
                status=status.HTTP_200_OK,
            )
        if event["type"] == "invoice.payment_succeeded":  # type: ignore
            # The payment succeeded and the user can be notified
            invoice = event["data"]["object"]  # type: ignore
            send_payment_mail(PaymentResult.Succeeded, invoice.metadata["user_id"])  # type: ignore
            return BackendResponse(
                f"Payment succeeded, sent email to user.",
                status=status.HTTP_200_OK,
            )

        return BackendResponse(f"Processed event {event['type']}", status=status.HTTP_200_OK)  # type: ignore
