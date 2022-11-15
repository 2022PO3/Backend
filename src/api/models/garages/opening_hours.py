from django.db import models

from src.api.models import DaysOfTheWeekEnum
from src.core.models import TimeStampMixin


class OpeningHours(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garages", on_delete=models.CASCADE)
    from_day = models.IntegerField(choices=DaysOfTheWeekEnum.choices)
    to_day = models.IntegerField(choices=DaysOfTheWeekEnum.choices)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
