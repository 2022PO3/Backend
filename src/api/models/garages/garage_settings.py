from django.db import models

from src.core.models import TimeStampMixin


class GarageSettings(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garages", on_delete=models.CASCADE)
    location = models.ForeignKey("api.Locations", on_delete=models.CASCADE)
    max_height = models.FloatField()
    max_width = models.FloatField()
    max_handicapped_lots = models.IntegerField()
