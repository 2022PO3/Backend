from django.db import models

from src.api.models import Garages, Locations
from src.core.models import TimeStampMixin


class GarageSettings(TimeStampMixin, models.Model):
    garage_id = models.ForeignKey(Garages, on_delete=models.CASCADE)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    max_height = models.FloatField()
    max_width = models.FloatField()
    max_handicapped_lots = models.IntegerField()
