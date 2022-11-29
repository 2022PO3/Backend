import datetime
from django.db import models

from src.api.models import ValutasEnum
from src.core.models import TimeStampMixin


class Price(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    price_string = models.CharField(max_length=192)
    duration = models.TimeField(default=datetime.time(0, 0, 0))
    price = models.FloatField()
    valuta = models.CharField(
        max_length=3, choices=ValutasEnum.choices, default=ValutasEnum.EURO
    )
    stripe_identifier = models.CharField(max_length=30, default="price_1M5XwcGRh96C3wQGkqJqXCmi")

    class Meta:
        db_table = "prices"
        app_label = 'api'
