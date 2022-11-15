from django.db import models

from src.core.models import TimeStampMixin


class ParkingLots(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garages", on_delete=models.CASCADE)
    floor_number = models.IntegerField()
    occupied = models.BooleanField()
    disabled = models.BooleanField(default=False)
