from rest_framework.permissions import BasePermission, SAFE_METHODS

from src.api.models import Garage
from src.api.models import Reservation

from django_otp.plugins.otp_totp.models import TOTPDevice


class OnlyGarageOwners(BasePermission):
    """
    Global permission to check if the user has the role garage owner.
    """

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_garage_owner


class IsGarageOwner(OnlyGarageOwners, BasePermission):
    """
    Object-level permission to only allow owners of the garage to edit it.
    Assumes the model instance has an `owner`-attribute.
    """

    def has_object_permission(self, request, view, pk: int) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        g = Garage.objects.get(pk=pk)
        return g.user == request.user


class IsUserDevice(BasePermission):
    """
    Object-level permission to only allow owners of a device to edit and/or delete it.
    Assumes the Device model has an `user-id`-attribute.
    """

    def has_object_permission(self, request, view, pk: int):
        if request.method in SAFE_METHODS:
            return True
        d = TOTPDevice.objects.get(pk=pk)
        return d.user_id == request.user.pk


class IsUserReservation(BasePermission):
    """
    Object-level  permission to only allow owners of a reservation to edit and/or delete it.
    Assumes the Reservation has an `user-id`-attribute.
    """

    def has_object_permission(self, request, view, pk: int):
        if request.method in SAFE_METHODS:
            return True
        r = Reservation.objects.get(pk=pk)
        return r.licence_plate.user.pk == request.user.pk
