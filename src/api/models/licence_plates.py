import datetime
from typing import Any
from django.db import models

from src.users.models import User
from src.core.models import TimeStampMixin

from django.views.decorators.http import require_http_methods


class LicencePlates(TimeStampMixin, models.Model):
    """
    Licence plate model, which is has a many-to-one relationship with `User` and a
    one-to-one relationship with `Garage`.

    The first relationship is needed for billing the correct person, the second is needed
    for calculating the correct amount (it's possible that different garages have different
    prices).

    If the `garage`-column is filled in, the `LicencePlate` is considered inside this
    parking garage.
    The `updated_at`-column is used to calculate the time inside the parking garage.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    garage = models.ForeignKey("api.Garages", on_delete=models.CASCADE, null=True)
    licence_plate = models.CharField(max_length=192, unique=True)

    @property
    def in_garage(self) -> bool:
        return self.garage == None

    @staticmethod
    def _register_licence_plate(licence_plate: str, garage_id: int) -> None:
        """
        This registers that a `LicencePlate` is entering a `Garage`. If the `LicencePlate`
        exists in the database, the `garage_id` is updated.

        If the `LicencePlate` doesn't exist in the database, a new dummy `User` with role 0
        is created, which is linked to the given `LicencePlate`.
        """

        queryset = LicencePlates.objects.filter(licence_plate=licence_plate)
        if not queryset:
            email = User.email_generator()
            password = User.objects.make_random_password(
                length=20,
                allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*();,./<>",
            )
            generated_user = User.objects.create_user(
                email=email,
                password=password,
                role=0,
            )
            LicencePlates.objects.create(
                user=generated_user,
                licence_plate=licence_plate,
                garage_id=garage_id,
                updated_at=datetime.datetime.now().astimezone().isoformat(),
            )
        else:
            queryset.update(
                garage_id=garage_id,
                updated_at=datetime.datetime.now().astimezone().isoformat(),
            )

    @staticmethod
    def _sign_out_licence_plate(licence_plate: "LicencePlates") -> None:
        """
        This signs out the `LicencePlate` from a `Garage`, setting its `garage_id` to `null`
        in the database. If the `LicencePlate` is associated with a dummy `User` of role 0,
        the `User` is also deleted from the database.
        """
        user = licence_plate.user
        if user.is_generated_user:
            licence_plate.delete()
            user.delete()
        else:
            licence_plate.garage = None
            licence_plate.save()

    @staticmethod
    def handle_licence_plate(params: dict[str, Any]) -> None:
        """
        This function handles the business logic for incoming licence plates.

        There are two main flows: the flow for entering vehicles and the flow for exiting
        vehicles. The flow itself is determined by the presence of the `garage_id` field in
        the database. If it's `null`, the `LicencePlate` is considered NOT in the garage,
        thus the `_register_licence_plate()` is called.

        The variable `params` contains the fields `garageId` and `licencePlate` from the
        `LicencePlateSerializer`.
        """

        licence_plate = params["licencePlate"]
        garage_id = params["garageId"]
        queryset = LicencePlates.objects.filter(licence_plate=licence_plate)
        if not queryset:
            LicencePlates._register_licence_plate(licence_plate, garage_id)
        else:
            lp = queryset[0]
            LicencePlates._register_licence_plate(
                licence_plate, garage_id
            ) if lp.in_garage else LicencePlates._sign_out_licence_plate(lp)
