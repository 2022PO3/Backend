import datetime

from datetime import datetime, timedelta
from django.db import models

from django.db import models
from django.utils import timezone
from src.api.models import Price
from src.core.utils import in_daterange
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

    @property
    def was_paid_for(self) -> bool:
        prices: list[Price] = Price.objects.filter(garage=self.garage)  # type: ignore
        prices = sorted(prices, key=lambda p: p.duration)
        if len(prices) == 0:
            return True
        return (timezone.now() - self.updated_at) > prices[0].duration

    def get_prices_to_pay(self) -> tuple[list[dict[str, str | int]], int]:
        # Fetch garage prices from database
        prices = Price.objects.filter(garage=self.garage)
        prices = sorted(prices, key=lambda p: p.duration, reverse=True)

        if len(prices) == 0:
            return tuple()

        # Get time the user has to pay for
        updated_at = self.updated_at
        time_to_pay = timezone.now() - updated_at

        # Go over each and reduce te time to pay by the largest possible amount
        preview_items = []
        for price in prices:

            item = {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                "price": price,
                "quantity": 0,
            }
            if price.duration >= timedelta(0):  # Make sure the loop completes
                while time_to_pay > price.duration:
                    time_to_pay -= price.duration
                    item["quantity"] += 1

            if item["quantity"] > 0:
                preview_items.append(item)

        # Calculate time in which app has to refresh
        refresh_time = prices[-1].duration - time_to_pay

        return preview_items, refresh_time  # type: ignore

    def can_reserve(self, from_date: datetime, to_date: datetime) -> bool:
        from src.api.models import Reservation

        user_reservations = Reservation.objects.filter(user=self.pk)
        return not any(
            map(
                lambda reservation: in_daterange(
                    reservation.from_date, reservation.to_date, from_date, to_date
                ),
                user_reservations,
            )
        )

    def delete(self) -> tuple[int, dict[str, int]]:
        from src.api.models import Reservation

        reservations = Reservation.objects.filter(licence_plate=self.pk)
        for reservation in reservations:
            reservation.delete()
        return super().delete()

    class Meta:
        db_table = "licence_plates"
        app_label = "api"
