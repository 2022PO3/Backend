from django.db import models

from src.api.models import Garages, ProvincesEnum
from src.core.models import TimeStampMixin


class Locations(TimeStampMixin, models.Model):
    garage_id = models.ForeignKey(Garages, on_delete=models.CASCADE)
    country = models.CharField(max_length=192)
    province = models.CharField(max_length=3, choices=ProvincesEnum.choices)
    municipality = models.CharField(max_length=192)
    post_code = models.IntegerField()
    street = models.CharField(max_length=192)
    number = models.IntegerField()
