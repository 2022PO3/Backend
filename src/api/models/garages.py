from django.db import models
from src.users.models import User
from src.core.models import TimeStampMixin


class Garages(TimeStampMixin, models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=192)

    @property
    def is_full(self) -> bool:
        from src.api.models.parking_lots import ParkingLots

        parking_lots = ParkingLots.objects.filter(garage_id=self.id)
        return len(parking_lots.filter(occupied=True)) == len(parking_lots)

    @property
    def unoccupied_lots(self) -> int:
        from src.api.models.parking_lots import ParkingLots

        return len(ParkingLots.objects.filter(garage_id=self.id).filter(occupied=True))

    @property
    def parking_lots(self) -> int:
        from src.api.models.parking_lots import ParkingLots

        return len(ParkingLots.objects.filter(garage_id=self.id))
