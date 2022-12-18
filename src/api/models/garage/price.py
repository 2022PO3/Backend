import datetime
from os import getenv
import stripe
from django.db import models

from src.api.models import ValutasEnum
from src.core.models import TimeStampMixin

stripe.api_key = getenv("STRIPE_SECRET_KEY")
publishableKey = getenv("STRIPE_PUBLISHABLE_KEY")

class Price(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    price_string = models.CharField(max_length=192)
    duration = models.DurationField(default=datetime.timedelta(hours=1))
    price = models.FloatField()
    valuta = models.CharField(
        max_length=3, choices=ValutasEnum.choices, default=ValutasEnum.EURO
    )
    stripe_identifier = models.CharField(
        max_length=30, default="price_1M5XwcGRh96C3wQGkqJqXCmi"
    )

    def delete_stripe_price(self) -> None:
        stripe.Price.modify(
            self.stripe_identifier,
            active=False,
        )

    class Meta:
        db_table = "prices"
        app_label = "api"
