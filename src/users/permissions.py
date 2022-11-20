from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from src.api.models import Garage, OpeningHour, ParkingLot, GarageSettings


class IsGarageOwner(BasePermission):
    """
    Object-level permission to only allow owners of the garage to edit it.
    Assumes the model instance has an `owner`-attribute.
    """

    def has_object_permission(self, request: Request, view, obj: int) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        g = Garage.objects.get(pk=obj)
        return g.owner == request.user
