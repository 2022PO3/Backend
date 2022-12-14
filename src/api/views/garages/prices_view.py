import stripe
from django.http import Http404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from src.api.serializers.garages.price_serializer import CreatePriceSerializer
from src.core.exceptions import DeletionException
from src.core.utils import create_stripe_price
from src.core.utils.stripe_endpoints import delete_stripe_price
from src.core.views import (
    BackendResponse,
    _OriginAPIView,
    GetObjectMixin,
    parse_frontend_json, PkAPIView,
)
from src.api.models import Price
from src.api.serializers import PriceSerializer
from src.users.permissions import IsGarageOwner


class GaragePricesView(PkAPIView):
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

    def post(self, request: Request, pk: int, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp

        price_data = parse_frontend_json(request)
        price_data['garage_id'] = pk
        create_price_serializer = CreatePriceSerializer(data=price_data)  # type: ignore
        if create_price_serializer.is_valid():
            # Create price on stripe servers
            try:
                price = create_stripe_price(create_price_serializer.data, pk)
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
            new_price_data['stripe_identifier'] = price.stripe_id
            price_serializer = PriceSerializer(data=new_price_data)

            if price_serializer.is_valid():
                price_serializer.save()
                return BackendResponse(
                    price_serializer.data, status=status.HTTP_201_CREATED
                )
            return BackendResponse(
                price_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return BackendResponse(
            create_price_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class PkPricesView(_OriginAPIView, GetObjectMixin):
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
        if (resp := super().put(request, format)) is not None:
            return resp
        data = parse_frontend_json(request)

        try:
            price = self.get_object(Price, pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [f"The Price with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PriceSerializer(price, data=data)  # type: ignore
        if serializer.is_valid():
            try:
                self.check_object_permissions(
                    request, serializer.validated_data["garage_id"]  # type: ignore
                )
            except KeyError:
                pass

            try:
                # Stripe does not support changing values in Prices,
                # delete the old price and create the new one
                delete_stripe_price(price)

                stripe_price = create_stripe_price(serializer.validated_data, price.garage.pk)

                serializer.save()
                
                price.stripe_identifier = stripe_price.stripe_id
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
        if (resp := super().delete(request, format)) is not None:
            return resp
        try:
            price = self.get_object(Price, pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [f"The Price with pk `{pk}` does not exist,"],
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            self.check_object_permissions(
                request, price.garage.pk  # type: ignore
            )
        except KeyError:
            pass

        try:
            delete_stripe_price(price)
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

        try:
            price.delete()
        except DeletionException as e:
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        return BackendResponse(None, status=status.HTTP_204_NO_CONTENT)
