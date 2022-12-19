from datetime import datetime
from random import randint

from django.db import models

from src.core.settings import OFFSET
from src.core.models import TimeStampMixin
from src.core.exceptions import DeletionException


class Garage(TimeStampMixin, models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    garage_settings = models.ForeignKey("api.GarageSettings", on_delete=models.CASCADE)
    name = models.CharField(max_length=192)
    entered = models.IntegerField(default=0)

    @property
    def increment_entered(self) -> None:
        self.entered += 1
        self.save()

    @property
    def decrement_entered(self) -> None:
        self.entered -= 1
        self.save()

    def delete(self) -> tuple[int, dict[str, int]]:
        from src.api.models import (
            OpeningHour,
            Price,
            Reservation,
            LicencePlate,
        )

        if not Reservation.objects.filter(garage_id=self.pk):
            raise DeletionException(
                "Garage cannot be deleted due to existing reservations in this garage."
            )
        if not LicencePlate.objects.filter(garage_id=self.pk):
            raise DeletionException(
                "Garage cannot be deleted due to existing licence plates in this garage."
            )
        garage_prices = Price.objects.filter(garage=self)
        for price in garage_prices:
            price.delete()
        garage_opening_hours = OpeningHour.objects.filter(garage=self)
        for opening_hour in garage_opening_hours:
            opening_hour.delete()
        garage_parking_lots = self.parking_lots()
        for parking_lot in garage_parking_lots:
            parking_lot.delete()
        return super().delete()

    def parking_lots(self) -> list:
        from src.api.models import ParkingLot

        return list(ParkingLot.objects.filter(garage=self))

    def reservations(self, pls: list | None = None) -> int:
        """
        Returns the amount of booked parking lots in the garage for a user with default park time.
        """
        if pls is None:
            pls = self.parking_lots()
        return len(list(filter(lambda pl: pl.booked(), pls)))

    def occupied_lots(self, from_date: datetime, to_date: datetime) -> int:
        """
        Returns the amount of occupied spots for a given startTime and endTime, i.e.
        the parking lots which are physically occupied and parking lots which are
        reserved.
        """
        pls = self.parking_lots()
        occupied_lots = len(list(filter(lambda pl: pl.occupied, pls)))
        reserved_lots = self.reservations(pls)
        return occupied_lots + reserved_lots

    def get_last_entered(self):
        """
        Gets the last entered licence plate of a garage.
        """
        from src.api.models import LicencePlate

        entered_lps = LicencePlate.objects.filter(garage=self)
        return min(entered_lps, key=lambda lp: abs(datetime.now() - lp.entered_at))  # type: ignore

    def get_random(
        self,
        from_date: datetime,
        end_date: datetime,
    ):
        """
        Returns a random free parking lot from the garage.
        """
        pls = list(
            filter(
                lambda pl: pl.available(from_date, end_date),
                self.parking_lots(),
            )
        )
        return pls[randint(0, len(pls))]

    class Meta:
        db_table = "garages"
        app_label = "api"
