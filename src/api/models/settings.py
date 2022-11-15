from django.db import models

from src.core.models import TimeStampMixin
from src.api.models import ProvincesEnum


class Settings(TimeStampMixin, models.Model):
    fav_garage = models.ForeignKey("api.Garages", on_delete=models.CASCADE)
    location = models.CharField(
        max_length=3,
        choices=ProvincesEnum.choices,
        default=ProvincesEnum.__empty__,
    )
