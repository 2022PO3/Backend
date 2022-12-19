from datetime import timedelta, datetime

from django.db import models

from src.core.models import TimeStampMixin


class Reservation(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    licence_plate = models.ForeignKey("api.LicencePlate", on_delete=models.CASCADE)
    parking_lot = models.ForeignKey("api.ParkingLot", on_delete=models.CASCADE)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    showed = models.BooleanField(default=False)

    def reassign(self) -> None:
        from src.api.models import ParkingLot

        pl = ParkingLot.get_random(self.garage.pk, self.from_date, self.to_date)
        self.user.notify(
            "Parking lot reassignment",
            f"Someone else parked on your reserved parking lot, thus it bas been reassigned from {self.parking_lot.parking_lot_no} to {pl.parking_lot_no}. The time of the reservation remains unchanged.",
        )
        self.parking_lot = pl
        self.save()

    @property
    def set_showed(self) -> None:
        """
        Sets the `showed` attribute of the reservation if the user showed up to the
        reservation.
        Showed attribute is set if the user showed up 30 mins in advance and before the half
        of the end of the reservation.
        """
        valid_before_time: datetime = self.from_date - timedelta(minutes=30)
        valid_between_time: datetime = (
            self.from_date + (self.to_date - self.from_date) / 2
        )
        if valid_before_time <= datetime.now().astimezone() <= valid_between_time:
            self.showed = True
            self.save()

    class Meta:
        db_table = "reservations"
        app_label = "api"
