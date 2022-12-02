from django.db import models
from src.core.models import TimeStampMixin


class Garage(TimeStampMixin, models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    garage_settings = models.ForeignKey("api.GarageSettings", on_delete=models.CASCADE)
    name = models.CharField(max_length=192)

    @property
    def is_full(self) -> bool:
        from src.api.models.garages.parking_lot import ParkingLot

        parking_lots = ParkingLot.objects.filter(garage_id=self.pk)
        return len(parking_lots.filter(occupied=True)) == len(parking_lots)

    @property
    def unoccupied_lots(self) -> int:
        from src.api.models.garages.parking_lot import ParkingLot

        return len(ParkingLot.objects.filter(garage_id=self.pk).filter(occupied=False))

    @property
    def parking_lots(self) -> int:
        from src.api.models.garages.parking_lot import ParkingLot

        return len(ParkingLot.objects.filter(garage_id=self.pk))

    class Meta:
        db_table = "garages"
        app_label = "api"
