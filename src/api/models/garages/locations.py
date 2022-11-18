from django.db import models

from src.api.models import ProvincesEnum
from src.core.models import TimeStampMixin


class Locations(TimeStampMixin, models.Model):
    country = models.CharField(max_length=192)
    province = models.CharField(max_length=3, choices=ProvincesEnum.choices)
    municipality = models.CharField(max_length=192)
    post_code = models.IntegerField()
    street = models.CharField(max_length=192)
    number = models.IntegerField()
