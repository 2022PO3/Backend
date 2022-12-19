from datetime import datetime, timedelta
from random import randint
from django.db import models

from src.core.settings import OFFSET
from src.core.utils import in_daterange
from src.core.models import TimeStampMixin


class ParkingLotManager(models.Manager):
    """
    Custom manager for `ParkingLot`-class, which implements the `.is_available()`-manager
    function.
    """

    def is_available(self, pk: int, start_time: datetime, end_time: datetime):
        for pl in (pls := super().get_queryset().filter(garage_id=pk)):
            pl.booked = pl.booked(start_time, end_time)
            pl.save()
        return pls


class ParkingLot(TimeStampMixin, models.Model):
    """
    Model for a single parking lot with the following attributes:
        - `garage`: garage where the parking lots belongs;
        - `parking_lot_no`: the number of the parking lot in the garage;
        - `floor_number`: the floor on which the parking lot resides in the garage;
        - `occupied`: indicates if the parking lot is occupied at the given time (note that a parking lot is occupied both if it holds a car or when it's booked);
        - `disabled`: indicates if the parking lot is disabled by the garage owner;
        - `booked`: indicates whether the parking lot is booked in a given time frame.
    """

    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    parking_lot_no = models.IntegerField()
    floor_number = models.IntegerField()
    occupied = models.BooleanField()
    disabled = models.BooleanField(default=False)

    def booked(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> bool:
        if start_time is None or end_time is None:
            return not self.is_available(
                datetime.now(), datetime.now() + timedelta(hours=2)
            )
        return not self.is_available(start_time, end_time)

    objects = ParkingLotManager()

    class Meta:
        unique_together = ("parking_lot_no", "garage")
        db_table = "parking_lots"
        app_label = "api"

    def is_available(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Returns a boolean which indicates if the given parking lot with `pl_pk` is available in
        the time range from `start_time` to `end_time`.
        """
        from src.api.models import Reservation

        # When a ParkingLot is occupied, this offset will be added to the time when the request is
        # made.
        pl_reservations = Reservation.objects.filter(parking_lot=self, showed=False)
        return not any(
            map(
                lambda reservation: in_daterange(
                    reservation.from_date, reservation.to_date, start_time, end_time
                ),
                pl_reservations,
            )
        )

    def reassign(self) -> None:
        """
        Reassigns a parking lot if it is reserved and someone - who don't made the reservation -
        parks within eight hours of the start of the reservation. The reservation's parking lot
        is reassigned.

        The function automatically gets the last entered licence plate.
        """
        from src.api.models import Reservation, LicencePlate

        pl_reservations = filter(
            lambda r: r.from_date > datetime.now(),
            Reservation.objects.filter(parking_lot=self),
        )
        pl_next_reservation = list(
            filter(
                lambda r: (r.from_date - datetime.now()) < OFFSET,
                pl_reservations,
            )
        )
        if pl_next_reservation:
            r = pl_next_reservation[0]
            if r.licence_plate.licence_plate != LicencePlate.get_last_entered(
                self.garage.pk
            ):
                r.reassign()

    @classmethod
    def get_random(
        cls,
        garage_id: int,
        from_date: datetime,
        end_date: datetime,
    ) -> "ParkingLot":
        pls = list(
            filter(
                lambda pl: not pl.booked,
                cls.objects.is_available(
                    garage_id,
                    from_date,
                    end_date,
                ),
            )
        )
        return pls[randint(0, len(pls))]
