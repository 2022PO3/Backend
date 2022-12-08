from django.db import models
from django.utils import timezone

from src.core.models import TimeStampMixin

from django.core.validators import MaxValueValidator, MinValueValidator

class Card(TimeStampMixin, models.Model):

    number = models.CharField(max_length=16)
    exp_month = models.IntegerField(validators=[MaxValueValidator(12), MinValueValidator(0)])
    exp_year = models.IntegerField(validators=[MinValueValidator(timezone.now().year - 1)])
    cvc = models.CharField(max_length=3)

    class Meta:
        app_label = 'api'
