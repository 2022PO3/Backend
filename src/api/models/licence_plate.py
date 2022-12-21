from datetime import timedelta, datetime
from django.db import models
from django.db import models
from django.utils import timezone

from src.api.models import Price
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
    The `paid_at`-column is used to calculate the time inside the parking garage.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE, null=True)
    licence_plate = models.CharField(max_length=192, unique=True)
    enabled = models.BooleanField(default=False)
    entered_at = models.DateTimeField(null=True)
    paid_at = models.DateTimeField(null=True)

    @property
    def in_garage(self) -> bool:
        return self.garage == None

    @property
    def can_leave(self) -> bool:
        return len(self.get_prices_to_pay()[0]) == 0

        # prices: list[Price] = Price.objects.filter(garage=self.garage)  # type: ignore
        # prices = sorted(prices, key=lambda p: p.duration)
        # if not len(prices):
        #     return True
        # if self.paid_at is not None:
        #     print(timezone.now() - self.paid_at)
        #     return (timezone.now() - self.paid_at) > prices[0].duration
        # if self.entered_at is not None:
        #     return (timezone.now() - self.entered_at) > prices[0].duration
        # return False

    def can_enter(self, garage) -> bool:
        """
        Determines if the licence plate can enter a given garage at the time of execution.
        """
        from src.api.models import Reservation

        lp_reservations = Reservation.objects.filter(garage=garage, licence_plate=self)
        if not lp_reservations:
            return False
        lp_reservation = min(
            lp_reservations,
            key=lambda r: abs(datetime.now().astimezone() - r.from_date),
        )
        if (
            lp_reservation.from_date - timedelta(minutes=30)
            <= datetime.now().astimezone()
            <= lp_reservation.from_date
            + (lp_reservation.to_date - lp_reservation.from_date) / 2
        ):
            lp_reservation.set_showed
            return True
        else:
            return False

    def get_prices_to_pay(self) -> tuple[list[dict[str, str | int]], int]:
        # Fetch garage prices from database
        prices = Price.objects.filter(garage=self.garage)
        prices = filter(lambda p: p.duration > timedelta(0), prices)
        prices = sorted(prices, key=lambda p: p.duration, reverse=True)

        if len(prices) == 0:
            return [], -1

        # Get time the user has to pay for
        if self.paid_at is not None:
            # If the user pays for the second time.
            time_to_pay = timezone.now() - self.paid_at
        elif self.entered_at is not None:
            # If the user pays for the first time.
            time_to_pay = timezone.now() - self.entered_at
        else:
            time_to_pay = timedelta(0)
        print(timezone.now(), self.paid_at)
        print('time to pay:', time_to_pay)
        # Go over each and reduce the time to pay by the largest possible amount
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
        from src.core.utils import overlap

        user_reservations = Reservation.objects.filter(user=self.pk)
        return not any(
            map(
                lambda reservation: overlap(
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
