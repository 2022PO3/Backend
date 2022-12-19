from random import randint
from datetime import datetime
from django.db import models

from src.core.settings import OFFSET
from src.core.utils import in_daterange
from src.core.models import TimeStampMixin
from src.api.models.user.reservation import Reservation


class ParkingLotManager(models.Manager):
    """
    Custom manager for `ParkingLot`-class, which implements the `.is_available()`-manager
    function.
    """

    def is_available(self, pk: int, start_time: datetime, end_time: datetime):
        for pl in (pls := super().get_queryset().filter(garage_id=pk)):
            pl.available = pl.available(start_time, end_time)
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
    licence_plate = models.ForeignKey("api.LicencePlate", on_delete=models.CASCADE)
    disabled = models.BooleanField(default=False)

    def booked(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> bool:
        if start_time is None or end_time is None:
            return not self._has_reservation(datetime.now(), datetime.now() + OFFSET)
        return not self._has_reservation(start_time, end_time)

    objects = ParkingLotManager()

    class Meta:
        unique_together = ("parking_lot_no", "garage")
        db_table = "parking_lots"
        app_label = "api"

    def available(
        self,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> bool:
        """
        Returns if the parking lot is available within the given time frame.
        """
        if from_date is None or to_date is None:
            from_date = datetime.now()
            to_date = from_date + OFFSET
        occupied_until = self._occupied_until
        if self._has_reservation(from_date, to_date):
            return False
        elif occupied_until is not None:
            return occupied_until < from_date  # type: ignore
        return True

    def reassign(self) -> None:
        """
        Reassigns a parking lot if it is reserved and someone - who didn't made the reservation -
        parks within eight hours of the start of the reservation. The reservation's parking lot
        is reassigned.
        """
        from src.api.models import Reservation

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
            if r.licence_plate.licence_plate != self.garage.get_last_entered():
                r.reassign()

    def set_lp(self) -> None:
        """
        Sets the licence plate which entered the parking lots, based on the last car which has entered the parking lot.
        """
        lp = self.garage.get_last_entered()
        self.licence_plate = lp
        self.save()

    def _occupied_until(self) -> datetime | None:
        if not self.occupied:
            return None
        reservation = self._has_now_reservation()
        if reservation is not None:
            return reservation.to_date
        return self.licence_plate.entered_at + OFFSET  # type: ignore

    def _has_reservation(self, from_date: datetime, to_date: datetime) -> bool:
        """
        Returns if the parking lot has a reservation for the given time frame.
        """
        reservations = self._get_reservations(valid=True)
        return not any(
            map(
                lambda reservation: in_daterange(
                    reservation.from_date, reservation.to_date, from_date, to_date
                ),
                reservations,
            )
        )

    def _has_now_reservation(self) -> Reservation | None:
        """
        Returns if the parking lot has a reservation for the moment the function is called.
        """
        pl_reservations = self._get_reservations()
        reservation_now = list(
            filter(
                lambda r: r.from_date <= datetime.now().astimezone() <= r.to_date,
                pl_reservations,
            )
        )

        return reservation_now[0] if reservation_now else None

    def _get_reservations(self, *, valid=False) -> list[Reservation]:
        """
        Returns alls the reservations for the parking lot.
        """
        reservations = list(Reservation.objects.filter(parking_lot=self))
        if not valid:
            return reservations
        else:
            return list(filter(lambda pl: pl.is_valid, reservations))
