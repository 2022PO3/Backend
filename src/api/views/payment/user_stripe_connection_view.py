# Create a new Customer
import stripe
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.request import Request

from src.api.serializers.card_serializer import CardSerializer
from src.core.utils import to_snake_case
from src.core.utils.stripe_endpoints import create_stripe_customer, remove_stripe_customer
from src.core.views import _OriginAPIView, BackendResponse, _dict_key_to_case


class UserStripeConnectionView(_OriginAPIView):
    """
    View for adding or removing a customer for stripe. The customers are necessary to make automatic charges. Each user
    automatically is assigned a default payment method using the provided card details.

    Stripe has some default testing cards to recreate successful and failed payment attempts:
    https://stripe.com/docs/testing
    """

    origins = ["web", "app"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp

        if not request.user.has_automatic_payment:
            card_data = _dict_key_to_case(JSONParser().parse(request), to_snake_case)

            serializer: CardSerializer = CardSerializer(data=card_data)
            if serializer.is_valid():
                try:

                    stripe_identifier = create_stripe_customer(request.user, serializer.validated_data)

                    request.user.stripe_identifier = stripe_identifier
                    request.user.save()

                    return BackendResponse('Added user to Stripe customers.', status=status.HTTP_201_CREATED)
                except ValidationError as e:
                    return BackendResponse(e.error_list, status=status.HTTP_400_BAD_REQUEST)
                except stripe.error.InvalidRequestError as e:
                    return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
                except stripe.error.StripeError as e:
                    return BackendResponse(['Something went wrong communicating with Stripe.', str(e)],
                                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return BackendResponse(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return BackendResponse(
                ['User is already a customer on Stripe, remove the old customer before creating a new one.'],
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().delete(request, format)) is not None:
            return resp

        if request.user.has_automatic_payment:
            try:
                remove_stripe_customer(request.user)
                request.user.stripe_identifier = None
                request.user.save()
                return BackendResponse('Removed customer from Stripe', status=status.HTTP_200_OK)
            except stripe.error.InvalidRequestError as e:
                return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as e:
                return BackendResponse(['Something went wrong communicating with Stripe.', str(e)],
                                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return BackendResponse(['User is not connected to Stripe.'], status=status.HTTP_400_BAD_REQUEST)
