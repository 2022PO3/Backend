from datetime import timedelta
from os import getenv
import stripe
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models

from src.api.models import ValutasEnum
from src.core.models import TimeStampMixin

stripe.api_key = getenv("STRIPE_SECRET_KEY")
publishableKey = getenv("STRIPE_PUBLISHABLE_KEY")

def validate_greater_than_zero(value):
    if value <= 0:
        raise ValidationError(
            _('%(value)s should be greater than 0.'),
            params={'value': value},
        )

def validate_duration_greater_than_zero(value):
    if value <= timedelta(0):
        raise ValidationError(
            _('%(value)s should be greater than 0.'),
            params={'value': value},
        )

class Price(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    price_string = models.CharField(max_length=192)
    duration = models.DurationField(default=timedelta(hours=1), validators=[validate_duration_greater_than_zero])
    price = models.FloatField(validators=[validate_greater_than_zero])
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
