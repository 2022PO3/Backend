import stripe
from django.http import Http404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.api.serializers.garages.price_serializer import CreatePriceSerializer
from src.core.utils import update_stripe_price, create_stripe_price
from src.core.views import (
    BackendResponse,
    _OriginAPIView,
    GetObjectMixin,
    parse_frontend_json,
)
from src.api.models import Price
from src.api.serializers import PriceSerializer
from src.users.permissions import IsGarageOwner


class PricesView(_OriginAPIView):
    """
    A view class which renders all the prices for a given garage with `pk`.
    """

    origins = ["app", "web"]

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp

        price_data = parse_frontend_json(request)
        create_price_serializer = CreatePriceSerializer(data=price_data)  # type: ignore

        if create_price_serializer.is_valid():
            # Create price on stripe servers
            try:
                price = create_stripe_price(create_price_serializer.data)
            except stripe.error.InvalidRequestError as e:
                return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as e:
                return BackendResponse(['Something went wrong communicating with Stripe.', str(e)], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return BackendResponse(
                    [f"Failed to create price on Stripe servers: {e}"],
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Add price to database
            price_data = JSONParser().parse(price)
            price_serializer = PriceSerializer(data=price_data)

            if price_serializer.is_valid():
                price_serializer.save()
            return BackendResponse(
                create_price_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return BackendResponse(
            create_price_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class PutPricesView(GetObjectMixin, _OriginAPIView):

    permission_classes = [IsGarageOwner]
    origins = ["web", "app"]

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            data = Price.objects.filter(garage_id=pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [
                    f"The corresponding price with 'pk' `{pk}` does not exist.",  # type: ignore
                ],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PriceSerializer(data, many=True)  # type: ignore
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().put(request, format)) is not None:
            return resp
        data = parse_frontend_json(request)

        try:
            object = self.get_object(Price, pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [f"The Price with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PriceSerializer(object, data=data)  # type: ignore
        if serializer.is_valid():
            try:
                self.check_object_permissions(
                    request, serializer.validated_data["garage_id"]  #  type: ignore
                )
            except KeyError:
                pass

            try:
                update_stripe_price(serializer.data)
            except stripe.error.InvalidRequestError as e:
                return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as e:
                return BackendResponse(['Something went wrong communicating with Stripe.', str(e)], status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return BackendResponse(
                    [f"Failed to update price on Stripe servers: {e}"],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            serializer.save()

            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
