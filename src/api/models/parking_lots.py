from django.db import models
from src.api.models.garages import Garages


class ParkingLots(models.Model):
    garage = models.ForeignKey(Garages, on_delete=models.CASCADE)
    floor_number = models.IntegerField()
    occupied = models.BooleanField()
