from django.db import models
from django.utils import timezone
from src.api.models.garages.price import Price
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

    @property
    def in_garage(self) -> bool:
        return self.garage == None

    @property
    def was_paid_for(self) -> bool:
        prices: list[Price] = Price.objects.filter(garage=self.garage)
        prices = sorted(prices, key=lambda p: p.duration)
        if len(prices) == 0:
            return True
        return (timezone.now() - self.updated_at) > prices[0].duration

    class Meta:
        db_table = "licence_plates"
        app_label = "api"
