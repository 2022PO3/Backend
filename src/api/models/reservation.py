from django.db import models

from src.api.models import LicencePlate
from src.core.models import TimeStampMixin


class Reservation(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    licence_plate = models.ForeignKey("api.LicencePlate", on_delete=models.CASCADE)
    parking_lot = models.ForeignKey("api.ParkingLot", on_delete=models.CASCADE)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()

    class Meta:
        db_table = "reservations"
        app_label = "api"
