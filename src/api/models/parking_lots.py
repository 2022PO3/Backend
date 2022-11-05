from django.db import models

from src.api.models.garages import Garages
from src.core.models import TimeStampMixin


class ParkingLots(TimeStampMixin, models.Model):
    garage = models.ForeignKey(Garages, on_delete=models.CASCADE)
    floor_number = models.IntegerField()
    occupied = models.BooleanField()
