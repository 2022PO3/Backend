from django.http import Http404
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from src.core.views import _OriginAPIView, BackendResponse, GetObjectMixin
from src.users.models import User
from src.users.permissions import IsUserDevice


def get_user_totp_device(user: User, confirmed=None) -> TOTPDevice | None:
    devices = devices_for_user(user, confirmed=confirmed)  # type: ignore

    for device in devices:
        if isinstance(device, TOTPDevice):
            return device


class TOTPCreateView(_OriginAPIView):
    """
    Use this endpoint to set up a new TOTP device
    """

    origins = ["web", "app"]

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        user = request.user
        device = get_user_totp_device(user)
        if not device:
            device = user.totpdevice_set.create(confirmed=False)
        url = device.config_url
        user.two_factor_validated = False
        user.save()
        return BackendResponse({"oauth_url": url}, status=status.HTTP_201_CREATED)


class TOTPVerifyView(_OriginAPIView):
    """
    Use this endpoint to verify/enable a TOTP device. Returns True if the code is valid and False otherwise.
    """

    origins = ["web", "app"]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token: str, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        user = request.user
        device = get_user_totp_device(user)
        print("Device", device)
        if not device == None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            user.two_factor_validated = True
            user.save()
            return BackendResponse({"response": True}, status=status.HTTP_200_OK)
        return BackendResponse({"response": False}, status=status.HTTP_401_UNAUTHORIZED)


class TOTPDeleteView(GetObjectMixin, _OriginAPIView):
    """
    A view class to delete a TOTP device on pk.
    """

    permission_classes = [IsUserDevice]
    origins = ["app", "web"]

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
        try:
            self.check_object_permissions(request, int(pk))
        except ValueError:
            return BackendResponse(["The value of `pk` has be an integer."])
        device.delete()  # type: ignore
        user = request.user
        user.two_factor_validated = None
        user.save()
        return BackendResponse(status=status.HTTP_204_NO_CONTENT)
