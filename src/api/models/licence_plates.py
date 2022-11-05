from django.db import models

from src.users.models import User
from src.api.models.garages import Garages
from src.core.models import TimeStampMixin


class LicencePlates(TimeStampMixin, models.Model):
    """
    Licence plate model, which is has a many-to-one relationship with `User` and a one-to-one relationship with `Garage`.

    The first relationship is needed for billing the correct person, the second is needed for calculating the correct amount (it's possible that different garages have different prices).

    If the `garage`-column is filled in, the `LicencePlate` is considered inside this parking garage.
    The `updated_at`-column is used to calculate the time inside the parking garage.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    garage = models.ForeignKey(Garages, on_delete=models.CASCADE, null=True)
    licence_plate = models.CharField(max_length=192, unique=True)
