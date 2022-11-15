from django.db import models

from src.api.models import Garages, ProvincesEnum
from src.users.models import User
from src.core.models import TimeStampMixin


class Settings(TimeStampMixin, models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    fav_garage_id = models.ForeignKey(Garages, on_delete=models.CASCADE)
    location = models.CharField(
        max_length=3, choices=ProvincesEnum.choices, default=ProvincesEnum.__empty__
    )
