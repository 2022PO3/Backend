import datetime
from django.db import models

from src.users.models import User
from src.core.models import TimeStampMixin


class LicencePlate(TimeStampMixin, models.Model):
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
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE, null=True)
    licence_plate = models.CharField(max_length=192, unique=True)
    enabled = models.BooleanField(default=False)

    @property
    def in_garage(self) -> bool:
        return self.garage == None

    def delete(self) -> tuple[int, dict[str, int]]:
        from src.api.models import Reservation

        reservations = Reservation.objects.filter(licence_plate=self.licence_plate)
        for reservation in reservations:
            reservation.delete()
        return super().delete()

    @staticmethod
    def _register_licence_plate(licence_plate: str, garage_id: int) -> int:
        """
        This registers that a `LicencePlate` is entering a `Garage`. If the `LicencePlate`
        exists in the database, the `garage_id` is updated.

        If the `LicencePlate` doesn't exist in the database, a new dummy `User` with role 0
        is created, which is linked to the given `LicencePlate`.
        """
        queryset = LicencePlate.objects.filter(licence_plate=licence_plate)
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
                is_active=1,
            )
            LicencePlate.objects.create(
                user=generated_user,
                licence_plate=licence_plate,
                garage_id=garage_id,
                updated_at=datetime.datetime.now().astimezone().isoformat(),
            )
            generated_user.generate_qr_code(password)
            generated_user.print_qr_code()
        else:
            queryset.update(
                garage_id=garage_id,
                updated_at=datetime.datetime.now().astimezone().isoformat(),
            )
        return 1

    @staticmethod
    def _sign_out_licence_plate(licence_plate: "LicencePlate") -> int:
        """
        This signs out the `LicencePlate` from a `Garage`, setting its `garage_id` to `null`
        in the database. If the `LicencePlate` is associated with a dummy `User` of role 0,
        the `User` is also deleted from the database.
        """
        user: User = licence_plate.user
        if user.is_generated_user:
            licence_plate.delete()
            user.delete_qr_code()
            user.delete()
        else:
            licence_plate.garage = None
            licence_plate.save()
        return 0

    @staticmethod
    def handle_licence_plate(licence_plate: str, garage_id: int) -> int:
        """
        This function handles the business logic for incoming licence plates.

        There are two main flows: the flow for entering vehicles and the flow for exiting
        vehicles. The flow itself is determined by the presence of the `garage_id` field in
        the database. If it's `null`, the `LicencePlate` is considered NOT in the garage,
        thus the `_register_licence_plate()` is called.

        The variable `params` contains the fields `garageId` and `licencePlate` from the
        `LicencePlateSerializer`.

        The output int-variable indicates if the licence plate is registered (1) or is signed
        out (0).
        """
        queryset = LicencePlate.objects.filter(licence_plate=licence_plate)
        if not queryset:
            return LicencePlate._register_licence_plate(licence_plate, garage_id)
        else:
            lp = queryset[0]
            return (
                LicencePlate._register_licence_plate(licence_plate, garage_id)
                if lp.in_garage
                else LicencePlate._sign_out_licence_plate(lp)
            )

    class Meta:
        db_table = "licence_plates"
        app_label = "api"
