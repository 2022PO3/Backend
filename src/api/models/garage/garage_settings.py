from django.db import models

from src.core.models import TimeStampMixin


class GarageSettings(TimeStampMixin, models.Model):
    location = models.ForeignKey("api.Location", on_delete=models.CASCADE)
    electric_cars = models.IntegerField(default=0)
    max_height = models.FloatField()
    max_width = models.FloatField()
    max_handicapped_lots = models.IntegerField()

    class Meta:
        db_table = "garage_settings"
        app_label = "api"
