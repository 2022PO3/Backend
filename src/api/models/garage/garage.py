from datetime import datetime, timedelta

from django.db import models
from django.db.models.query import QuerySet

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
            ParkingLot,
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
        garage_prices = Price.objects.filter(garage_id=self.pk)
        for price in garage_prices:
            price.delete()
        garage_opening_hours = OpeningHour.objects.filter(garage_id=self.pk)
        for opening_hour in garage_opening_hours:
            opening_hour.delete()
        garage_parking_lots = ParkingLot.objects.filter(garage_id=self.pk)
        for parking_lot in garage_parking_lots:
            parking_lot.delete()
        return super().delete()

    def parking_lots(self) -> QuerySet:
        from src.api.models import ParkingLot

        return ParkingLot.objects.filter(garage_id=self.pk)

    def reservations(self) -> int:
        """
        Returns the amount of booked parking lots in the garage.
        """
        from src.api.models import ParkingLot

        pls = ParkingLot.objects.is_available(
            self.pk,
            datetime.now(),
            datetime.now() + OFFSET,
        )

        return len(list(filter(lambda pl: pl.booked(), pls)))

    def occupied_lots(self, from_date: datetime, to_date: datetime) -> int:
        """
        Returns the amount of occupied spots for a given startTime and endTime, i.e.
        the parking lots which are physically occupied and parking lots which are
        reserved.
        """
        from src.api.models import ParkingLot

        parking_lots = ParkingLot.objects.filter(garage_id=self.pk)

        occupied_lots = len(list(filter(lambda pl: pl.occupied, parking_lots)))
        reserved_lots = len(
            list(filter(lambda pl: pl.is_available(from_date, to_date), parking_lots))
        )
        return occupied_lots + reserved_lots

    class Meta:
        db_table = "garages"
        app_label = "api"
