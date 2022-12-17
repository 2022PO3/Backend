from rest_framework.request import Request
from rest_framework.permissions import BasePermission, SAFE_METHODS

from src.api.models import Garage, Reservation, Notification

from django_otp.plugins.otp_totp.models import TOTPDevice


class OnlyGarageOwners(BasePermission):
    """
    Global permission to check if the user has the role garage owner.
    """

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_garage_owner or request.user.is_admin


class IsGarageOwner(OnlyGarageOwners, BasePermission):
    """
    Object-level permission to only allow owners of the garage to edit it.
    Assumes the model instance has an `owner`-attribute.
    """

    @staticmethod
    def has_object_permission(request: Request, g: int | Garage, obj=None) -> bool:
        print("exec")
        print(request, g, obj)
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        if isinstance(g, int):
            if obj is None:
                garage = Garage.objects.get(pk=g)
                return garage.user == request.user
            else:
                obj = obj.objects.get(pk=g)
                return obj.garage.user == request.user
        return g.user == request.user


class IsUserDevice(BasePermission):
    """
    Object-level permission to only allow owners of a device to edit and/or delete it.
    Assumes the Device model has an `user-id`-attribute.
    """

    def has_object_permission(self, request: Request, view, pk: int):
        if request.method in SAFE_METHODS:
            return True
        d = TOTPDevice.objects.get(pk=pk)
        return d.user_id == request.user.pk


class IsUserReservation(BasePermission):
    """
    Object-level  permission to only allow owners of a reservation to edit and/or delete it.
    Assumes the Reservation has an `user-id`-attribute.
    """

    def has_object_permission(self, request: Request, view, pk: int):
        if request.method in SAFE_METHODS:
            return True
        r = Reservation.objects.get(pk=pk)
        return r.licence_plate.user.pk == request.user.pk


class IsUserNotification(BasePermission):
    """
    Object-level permission to only allow owners of a notification to delete it. Assumes the Notification has an `user_id`-attribute.
    """

    def has_object_permission(self, request: Request, view, pk: int):
        if request.method in SAFE_METHODS:
            return True
        r = Notification.objects.get(pk=pk)
        return r.user.pk == request.user.pk
