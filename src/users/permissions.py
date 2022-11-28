from jwt.exceptions import DecodeError, ExpiredSignatureError

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import BasePermission, SAFE_METHODS

from src.api.models import Garage
from src.core.utils import decode_jwt
from src.core.views import BackendException


class OnlyGarageOwners(BasePermission):
    """
    Global permission to check if the user has the role garage owner.
    """

    def has_permission(self, request: Request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_garage_owner


class IsGarageOwner(OnlyGarageOwners, BasePermission):
    """
    Object-level permission to only allow owners of the garage to edit it.
    Assumes the model instance has an `owner`-attribute.
    """

    def has_object_permission(self, request: Request, view, pk: int) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        g = Garage.objects.get(pk=pk)
        return g.user == request.user


class HasJWTToken(BasePermission):
    """
    Global permission to only allow users with a proper JWT-token.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        try:
            jwt_token = request.headers["Authorization"]
        except KeyError:
            return False
        try:
            decoded_data = decode_jwt(jwt_token, "JWT_SECRET_2FA")
        except (ExpiredSignatureError, DecodeError, BackendException) as e:
            return False
        try:
            uid = decoded_data["uid"]
        except KeyError:
            return False
        return int(uid) == request.user.pk
