from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from src.api.models import Garages, OpeningHours, ParkingLots, GarageSettings


class IsGarageOwner(BasePermission):
    """
    Object-level permission to only allow owners of the garage to edit it.
    Assumes the model instance has an `owner`-attribute.
    """

    def has_object_permission(
        self, request: Request, view, obj: Garages | OpeningHours | ParkingLots
    ) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        if isinstance(obj, Garages):
            return obj.owner == request.user
        else:
            return obj.garage.owner == request.user
