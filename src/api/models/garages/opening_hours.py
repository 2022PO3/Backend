from django.db import models

from src.api.models import Garages, DaysOfTheWeekEnum
from src.core.models import TimeStampMixin


class OpeningHours(TimeStampMixin, models.Model):
    garage_id = models.ForeignKey(Garages, on_delete=models.CASCADE)
    day_from = models.IntegerField(choices=DaysOfTheWeekEnum.choices)
    day_to = models.IntegerField(choices=DaysOfTheWeekEnum.choices)
    hour_from = models.DateTimeField()
    hour_to = models.DateTimeField()
