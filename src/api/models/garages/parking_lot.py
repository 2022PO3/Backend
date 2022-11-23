from datetime import datetime, timedelta
from django.db import models
from src.core.models import TimeStampMixin


class ParkingLotManager(models.Manager):
    """
    Custom manager for `ParkingLot`-class, which implements the `.is_available()`-manager function.
    """

    def is_available(self, pk: int, start_time: datetime, end_time: datetime):
        for pl in (pls := super().get_queryset().filter(garage_id=pk)):
            pl.booked = pl.booked(start_time, end_time)
        return pls


class ParkingLot(TimeStampMixin, models.Model):
    """
    Model for a single parking lot with the following attributes:
        - `garage`: garage where the parking lots belongs;
        - `parking_lot_no`: the number of the parking lot in the garage;
        - `floor_number`: the floor on which the parking lot resides in the garage;
        - `occupied`: indicates if the parking lot is occupied at the given time (note that a parking lot is occupied both if it holds a car or when it's booked);
        - `disabled`: indicates if the parking lot is disabled by the garage owner.
    """

    garage = models.ForeignKey("api.Garage", on_delete=models.CASCADE)
    parking_lot_no = models.IntegerField()
    floor_number = models.IntegerField()
    occupied = models.BooleanField()
    disabled = models.BooleanField(default=False)

    def booked(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> bool:
        if start_time is None and end_time is None:
            return False
        return not parking_lot_is_available(self, start_time, end_time)  # type: ignore

    objects = ParkingLotManager()

    class Meta:
        unique_together = ("parking_lot_no", "garage")
        db_table = "parking_lots"
        app_label = "api"


def parking_lot_is_available(
    pl: ParkingLot, start_time: datetime, end_time: datetime
) -> bool:
    """
    Returns a boolean which indicates if the given parking lot with `pl_pk` is available in
    the time range from `start_time` to `end_time`.
    """
    from src.api.models import Reservation

    # When a ParkingLot is occupied, this offset will be added to the time when the request is
    # made.
    OFFSET = timedelta(hours=8)

    pl_reservations = Reservation.objects.filter(parking_lot=pl)
    if pl.occupied and not (
        start_time.timestamp()
        <= (datetime.utcnow() + OFFSET).timestamp()
        <= end_time.timestamp()
    ):
        return True
    elif pl.occupied and (
        start_time.timestamp()
        <= (datetime.utcnow() + OFFSET).timestamp()
        <= end_time.timestamp()
    ):
        return False
    else:
        if not pl_reservations:
            return True
        else:
            return not any(
                map(
                    lambda reservation: in_daterange(
                        reservation.from_date, reservation.to_date, start_time, end_time
                    ),
                    pl_reservations,
                )
            )


def in_daterange(st1: datetime, et1: datetime, st2: datetime, et2: datetime) -> bool:
    """
    Returns a boolean which indicates if the given date ranges overlap with each other.
    """
    return (
        st1 <= st2 <= et1 or st1 <= et2 <= et1 or st2 <= st1 <= et2 or st1 <= et2 <= et1
    )
