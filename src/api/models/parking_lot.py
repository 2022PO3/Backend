from django.db import models

from src.core.models import TimeStampMixin


class ParkingLot(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    parking_lot_no = models.IntegerField()
    floor_number = models.IntegerField()
    occupied = models.BooleanField()
    disabled = models.BooleanField(default=False)

    class Meta:
        db_table = "parking_lots"
        app_label = "api"
