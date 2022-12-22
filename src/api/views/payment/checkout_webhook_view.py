from os import getenv

from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.core.utils.payment_mails import PaymentResult, send_payment_mail
from src.core.views import BackendResponse
from src.users.models import User


import stripe


def complete_payment(metadata: dict) -> BackendResponse:
    metadata = metadata
    if "licence_plate" in metadata.keys() and "user_id" in metadata.keys():
        licence_plate = metadata["licence_plate"]
        user_id = metadata["user_id"]
    else:
        return BackendResponse(
            [
                "The required data to complete the order was not included in the session metadata."
            ],
            status=status.HTTP_400_BAD_REQUEST,
        )

    licence_plate = LicencePlate.objects.get(
        user=User.objects.get(pk=user_id), licence_plate=licence_plate
    )

    licence_plate.paid_at = timezone.now()

    licence_plate.save()
    return BackendResponse(["Completed order"], status=status.HTTP_200_OK)


class CheckoutWebhookView(APIView):
    """
    View class to listen for checkout updates from the stripe servers.
    """

    # The post request checks if the request comes from Stripe.
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
                payload, sig_header, getenv("STRIPE_CHECKOUT_WEBHOOK_KEY")  # type: ignore
            )
        except ValueError as e:
            # Invalid payload
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:  # type: ignore
            # Invalid signature
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:  # type: ignore
            print(str(e))
            BackendResponse(
                ["Something went wrong communicating with Stripe.", str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Handle the checkout.session.completed event
        if event["type"] == "checkout.session.completed":  # type: ignore
            session = event["data"]["object"]  # type: ignore

            # Save an order in your database, marked as 'awaiting payment'
            # create_order(session)

            # Check if the order is already paid (for example, from a card payment)
            # A delayed notification payment will have an `unpaid` status, as
            # you're still waiting for funds to be transferred from the customer's
            # account.
            if session.payment_status == "paid":
                # Fulfil the purchase
                send_payment_mail(PaymentResult.Succeeded, session.metadata["user_id"])  # type: ignore
                return complete_payment(session.metadata)

        elif event["type"] == "checkout.session.async_payment_succeeded":  # type: ignore
            session = event["data"]["object"]  # type: ignore

            # Fulfil the purchase
            send_payment_mail(PaymentResult.Succeeded, session.metadata["user_id"])  # type: ignore
            complete_payment(session.metadata)

        elif event["type"] == "checkout.session.async_payment_failed":  # type: ignore
            session = event["data"]["object"]  # type: ignore
            send_payment_mail(PaymentResult.CheckoutFailed, session.metadata["user_id"])  # type: ignore
            return BackendResponse(
                "Payment failed, notified user.",
                status=status.HTTP_200_OK,
            )

        # Passed signature verification
        return BackendResponse(
            f"Processed event: {event['type']}",  # type: ignore
            status=status.HTTP_200_OK,
        )
