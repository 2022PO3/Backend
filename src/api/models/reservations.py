from django.db import models

from src.core.models import TimeStampMixin


class Reservations(TimeStampMixin, models.Model):
    garage = models.ForeignKey("api.Garages", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parking_lot = models.ForeignKey("api.ParkingLots", on_delete=models.CASCADE)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
