from django.db import models

from src.core.models import TimeStampMixin
from src.core.exceptions import DeletionException


class Garage(TimeStampMixin, models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    garage_settings = models.ForeignKey("api.GarageSettings", on_delete=models.CASCADE)
    name = models.CharField(max_length=192)
    unoccupied_lots = models.IntegerField(default=0)

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

    @property
    def is_full(self) -> bool:
        from src.api.models import ParkingLot

        parking_lots = ParkingLot.objects.filter(garage_id=self.pk)
        return len(parking_lots.filter(occupied=True)) == len(parking_lots)

    @property
    def parking_lots(self) -> int:
        from src.api.models import ParkingLot

        return len(ParkingLot.objects.filter(garage_id=self.pk))

    class Meta:
        db_table = "garages"
        app_label = "api"
