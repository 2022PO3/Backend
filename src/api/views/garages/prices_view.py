import stripe
from django.http import Http404
from rest_framework import status
from rest_framework.request import Request

from src.api.serializers.garages.price_serializer import CreatePriceSerializer
from src.core.utils import create_stripe_price
from src.core.views import (
    BackendResponse,
    parse_frontend_json,
    PkAPIView,
    try_delete,
)
from src.api.models import Price, Garage
from src.api.serializers import PriceSerializer
from src.users.permissions import IsGarageOwner


class PricesDetailView(PkAPIView):
    """
    View class for getting, putting and deleting Prices with a given 'pk'.
    """

    permission_classes = [IsGarageOwner]
    origins = ["web", "app"]
    http_method_names = ["get", "put", "delete"]
    column = "price_id"
    model = Price
    serializer = PriceSerializer

    def put(self, request: Request, pk: int, format=None) -> BackendResponse:
        try:
            price: Price = self.get_object(Price, pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [f"The price with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, pk, Price)
        data = parse_frontend_json(request)
        serializer = PriceSerializer(price, data=data)  # type: ignore
        if serializer.is_valid():
            try:
                # Stripe does not support changing values in Prices,
                # delete the old price and create the new one
                price.delete_stripe_price()
                stripe_price = create_stripe_price(
                    serializer.validated_data, price.garage.pk
                )
                serializer.save()
                price.stripe_identifier = stripe_price.stripe_id
                price.save()
            except stripe.error.InvalidRequestError as e:  # type: ignore
                return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as e:  # type: ignore
                return BackendResponse(
                    ["Something went wrong communicating with Stripe.", str(e)],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            except Exception as e:
                return BackendResponse(
                    [f"Failed to update price on Stripe servers: {e}"],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request: Request, pk: int, format=None) -> BackendResponse:
        try:
            price: Price = self.get_object(Price, pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [f"The price with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, pk, Price)
        try:
            price.delete_stripe_price()
        except stripe.error.InvalidRequestError as e:  # type: ignore
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:  # type: ignore
            return BackendResponse(
                ["Something went wrong communicating with Stripe.", str(e)],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return BackendResponse(
                [f"Failed to update price on Stripe servers: {e}"],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return try_delete(price)


class PricesGarageView(PkAPIView):
    """
    A view class which renders all the prices for a given garage with `pk`.
    """

    origins = ["app", "web"]
    column = "garage_id"
    permission_classes = [IsGarageOwner]
    model = Price
    serializer = PriceSerializer
    return_list = True
    http_method_names = ["get", "post"]

    def get(self, request: Request, garage_pk: int, format=None) -> BackendResponse:
        return super().get(request, garage_pk, format)

    def post(self, request: Request, garage_pk: int, format=None) -> BackendResponse:
        try:
            garage: Garage = self.get_object(Garage, garage_pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [f"The {self.model.__name__} with pk `{garage_pk}` does not exist,"],  # type: ignore
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, garage_pk)
        price_data = parse_frontend_json(request)
        create_price_serializer = CreatePriceSerializer(data=price_data)  # type: ignore
        if create_price_serializer.is_valid():
            # Create price on stripe servers
            try:
                price = create_stripe_price(
                    create_price_serializer.validated_data, garage_pk
                )
            except stripe.error.InvalidRequestError as e:  # type: ignore
                return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.StripeError as e:  # type: ignore
                return BackendResponse(
                    ["Something went wrong communicating with Stripe.", str(e)],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            except Exception as e:
                return BackendResponse(
                    [f"Failed to create price on Stripe servers: {e}"],
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Add price to database
            new_price_data = create_price_serializer.data
            new_price_data["stripe_identifier"] = price.stripe_id
            price_serializer = PriceSerializer(data=new_price_data)  # type: ignore

            if price_serializer.is_valid():
                price_serializer.save(garage_id=garage_pk)
                return BackendResponse(
                    price_serializer.data, status=status.HTTP_201_CREATED
                )
            return BackendResponse(
                price_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return BackendResponse(
            create_price_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
