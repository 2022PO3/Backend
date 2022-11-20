from django.db import models

from src.api.models import DaysOfTheWeekEnum
from src.core.models import TimeStampMixin


class OpeningHour(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    from_day = models.IntegerField(choices=DaysOfTheWeekEnum.choices)
    to_day = models.IntegerField(choices=DaysOfTheWeekEnum.choices)
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    class Meta:
        db_table = "opening_hours"
        app_label = 'api'