from datetime import datetime
from typing import Any
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.models import LicencePlate
from src.api.serializers import LicencePlateSerializer, LicencePlateRPiSerializer
from src.core.views import (
    PkAPIView,
    BaseAPIView,
    BackendResponse,
    _OriginAPIView,
    parse_frontend_json,
)
from src.users.models import User


class LicencePlateDetailView(PkAPIView):
    """
    View class to delete or update a `LicencePlate` with the given `pk`.
    """

    origins = ["app", "web"]
    model = LicencePlate
    serializer = LicencePlateRPiSerializer
    user_id = True


class LicencePlateListView(BaseAPIView):
    """
    View class to get all the user's licence plates and to post new one.
    """

    origins = ["app", "web"]
    serializer = {"get": LicencePlateSerializer, "post": LicencePlateSerializer}
    model = LicencePlate
    get_user_id = True
    post_user_id = True


class RPiLicencePlateView(_OriginAPIView):
    """
    View class which handles POST-requests for licence plates from the Raspberry Pi.
    """

    permission_classes = [AllowAny]
    origins = ["rpi"]
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        data = parse_frontend_json(request)
        serializer = LicencePlateRPiSerializer(data=data)  # type: ignore
        if serializer.is_valid():
            if serializer.validated_data["licence_plate"] == "0AAA000":  # type: ignore
                return BackendResponse("OK", status=status.HTTP_200_OK)
            self.handle_licence_plate(
                serializer.data,
            )
            return BackendResponse(serializer.data, status=status.HTTP_201_CREATED)
        return BackendResponse(
            [serializer.errors],  # type: ignore
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _register_licence_plate(
        self, licence_plate: str, garage_id: int
    ) -> BackendResponse:
        """
        This registers that a `LicencePlate` is entering a `Garage`. If the `LicencePlate`
        exists in the database, the `garage_id` is updated.

        If the `LicencePlate` doesn't exist in the database, a new dummy `User` with role 0
        is created, which is linked to the given `LicencePlate`.
        """
        queryset = LicencePlate.objects.filter(licence_plate=licence_plate)
        now = datetime.now().astimezone().isoformat()
        if not queryset:
            email = User.email_generator()
            password = User.objects.make_random_password(
                length=30,
                allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*();,./<>",
            )
            generated_user = User.objects.create_user(
                email=email,
                password=password,
                role=0,
            )
            LicencePlate.objects.create(
                user=generated_user,
                licence_plate=licence_plate,
                garage_id=garage_id,
                updated_at=now,
                entered_at=now,
            )
            generated_user.generate_qr_code(password)
            generated_user.print_qr_code()
        else:
            queryset.update(garage_id=garage_id, updated_at=now, entered_at=now)
        return BackendResponse(
            f"Successfully registered licence plate {licence_plate}.",
            status=status.HTTP_200_OK,
        )

    def _sign_out_licence_plate(self, licence_plate: LicencePlate) -> BackendResponse:
        """
        This signs out the `LicencePlate` from a `Garage`, setting its `garage_id` to `null`
        in the database. If the `LicencePlate` is associated with a dummy `User` of role 0,
        the `User` is also deleted from the database.
        """
        user: User = licence_plate.user  # User.objects.get(pk=user_id)
        if licence_plate.was_paid_for:
            if user.is_generated_user:
                licence_plate.delete()
                user.delete()
            else:
                # Check if the user paid before trying to leave
                licence_plate.garage = None
                licence_plate.save()
            return BackendResponse(
                f"Successfully signed out licence plate {licence_plate}.",
                status=status.HTTP_200_OK,
            )
        elif user.has_automatic_payment:
            try:
                user.send_invoice(licence_plate)
                return BackendResponse(
                    f"Sent invoice to user of {licence_plate}.",
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return BackendResponse(
                    f"User needs to pay for {licence_plate} before leaving the garage and failed to sent invoice.",
                    status=status.HTTP_402_PAYMENT_REQUIRED,
                )

        return BackendResponse(
            f"User needs to pay for {licence_plate} before leaving the garage.",
            status=status.HTTP_402_PAYMENT_REQUIRED,
        )

    def handle_licence_plate(self, data: dict[str, Any]) -> BackendResponse:
        """
        This function handles the business logic for incoming licence plates.

        There are two main flows: the flow for entering vehicles and the flow for exiting
        vehicles. The flow itself is determined by the presence of the `garage_id` field in
        the database. If it's `null`, the `LicencePlate` is considered NOT in the garage,
        thus the `_register_licence_plate()` is called.

        The variable `params` contains the fields `garageId` and `licencePlate` from the
        `LicencePlateSerializer`.
        """
        licence_plate: str = data["licence_plate"]
        garage_id: int = data["garage_id"]
        queryset = LicencePlate.objects.filter(licence_plate=licence_plate)
        if not queryset:
            return self._register_licence_plate(licence_plate, garage_id)
        else:
            lp = queryset[0]
            return (
                self._register_licence_plate(licence_plate, garage_id)
                if lp.in_garage
                else self._sign_out_licence_plate(lp)
            )
