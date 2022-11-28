from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice

from rest_framework import status
from rest_framework.request import Request

from src.core.views import _OriginAPIView, BackendResponse
from src.users.models import User
from src.users.permissions import HasJWTToken


def get_user_totp_device(self, user: User) -> TOTPDevice | None:
    devices = devices_for_user(user)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device


class TOTPCreateView(_OriginAPIView):
    """
    Use this endpoint to set up a new TOTP device
    """

    origins = ["web", "app"]

    def get(self, request: Request, format=None):
        if (resp := super().get(request, format)) is not None:
            return resp
        user = request.user
        device = get_user_totp_device(self, user)
        if not device:
            device = user.totpdevice_set.create(confirmed=False)
        url = device.config_url
        return BackendResponse({"response": url}, status=status.HTTP_201_CREATED)


class TOTPVerifyView(_OriginAPIView):
    """
    Use this endpoint to verify/enable a TOTP device. Returns True if the code is valid and False otherwise.
    """

    origins = ["web", "app"]
    permission_classes = [HasJWTToken]

    def post(self, request: Request, token: str, format=None):
        if (resp := super().post(request, format)) is not None:
            return resp
        user = request.user
        device = get_user_totp_device(self, user)
        if not device == None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            return BackendResponse({"response": True}, status=status.HTTP_200_OK)
        return BackendResponse({"response": False}, status=status.HTTP_400_BAD_REQUEST)
