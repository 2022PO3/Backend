from django.db import models

from src.api.models import ValutasEnum
from src.core.models import TimeStampMixin


class Prices(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garages", on_delete=models.CASCADE)
    price_string = models.CharField(max_length=192)
    price = models.FloatField()
    valuta = models.CharField(
        max_length=3, choices=ValutasEnum.choices, default=ValutasEnum.EURO
    )
