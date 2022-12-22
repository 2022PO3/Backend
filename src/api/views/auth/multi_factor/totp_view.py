from typing import Iterable

from django.http import Http404
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from src.api.serializers import TOTPSerializer
from src.core.views import (
    _OriginAPIView,
    BackendResponse,
    GetObjectMixin,
    BaseAPIView,
    parse_frontend_json,
)
from src.users.models import User
from src.users.permissions import IsUserDevice


class TOTPDetailView(GetObjectMixin, _OriginAPIView):
    """
    A view class which handles PUT- and DELETE-requests of TOTP devices with a `pk`.
    """

    permission_classes = [IsUserDevice]
    origins = ["app", "web"]
    http_method_names = ["delete"]

    def delete(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().delete(request, format)) is not None:
            return resp
        try:
            device = self.get_object(TOTPDevice, pk)
        except Http404:
            return BackendResponse(
                [f"The device with pk {pk} does not exist."],
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, int(pk))
        device.delete()  # type: ignore
        request.user.disable_2fa()
        return BackendResponse(status=status.HTTP_204_NO_CONTENT)


class TOTPListView(BaseAPIView):
    """
    View class which handles GET- and POST-requests for TOTPDevices.
    """

    origins = ["web", "app"]
    serializer = {"get": TOTPSerializer, "post": TOTPSerializer}
    model = TOTPDevice
    get_user_id = True
    post_user_id = True
    http_method_names = ["get", "post"]

    def post(self, request: Request, format=None) -> BackendResponse:
        data = parse_frontend_json(request)
        serializer = TOTPSerializer(data=data)  # type: ignore
        user: User = request.user
        if serializer.is_valid():
            device = user.totpdevice_set.create(  # type: ignore
                name=serializer.validated_data["name"], confirmed=False  # type: ignore
            )
            if not user.two_factor:
                user.enable_2fa()
            url = device.config_url  # type: ignore
            return BackendResponse({"oauth_url": url}, status=status.HTTP_201_CREATED)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TOTPVerifyView(_OriginAPIView):
    """
    View class which handle verifying of TOTP-device codes. Returns True if the code is valid
    and False otherwise.
    """

    origins = ["web", "app"]
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token: str, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        user: User = request.user
        devices = self._get_totp_devices(user)
        for device in devices:
            if self._verify_and_confirm(user, device, token):
                return BackendResponse({"response": True}, status=status.HTTP_200_OK)
        return BackendResponse({"response": False}, status=status.HTTP_401_UNAUTHORIZED)

    def _verify_and_confirm(self, user: User, device: TOTPDevice, token: str) -> bool:
        if not device == None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            user.validated_2fa()
            return True
        return False

    def _get_totp_devices(self, user: User, confirmed=None) -> Iterable[TOTPDevice]:
        devices = devices_for_user(user, confirmed=confirmed)  # type: ignore
        return filter(lambda d: isinstance(d, TOTPDevice), devices)


class Disable2FAView(_OriginAPIView):
    """
    View class which handles disabling of 2FA for a user.
    """

    origins = ["web", "app"]
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp
        request.user.disable_2fa()
        return BackendResponse(None, status=status.HTTP_204_NO_CONTENT)
