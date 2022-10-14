from django.db import models
from src.api.models.garages import Garage


class ParkingLot(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, blank=False)
    floor_number = models.IntegerField(blank=False)
    occupied = models.BooleanField(blank=False)
