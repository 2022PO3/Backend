from django.db import models
from django.contrib.auth.models import User


class Garage(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

    def is_full(self) -> bool:
        parking_lots = self.objects.select_related("parking_lots")
        return len(parking_lots.filter(occupied=True)) == len(parking_lots)

    def unoccupied_lots(self) -> int:
        return len(self.objects.select_related("parking_lots").filter(occupied=True))
