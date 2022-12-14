from django.http import Http404
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from src.api.serializers import GetTOTPSerializer, PostTOTPSerializer
from src.core.views import (
    _OriginAPIView,
    BackendResponse,
    GetObjectMixin,
    BaseAPIView,
    parse_frontend_json,
)
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
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        data = parse_frontend_json(request)
        serializer = PostTOTPSerializer(data=data)  # type: ignore
        user: User = request.user
        device = get_user_totp_device(user)
        if device:
            return BackendResponse(
                ["You already have a 2FA device registered."],
                status=status.HTTP_400_BAD_REQUEST,
            )
        if serializer.is_valid():
            device = user.totpdevice_set.create(  # type: ignore
                name=serializer.validated_data["name"], confirmed=False  # type: ignore
            )
            user.enable_2fa()
            url = device.config_url  # type: ignore
            return BackendResponse({"oauth_url": url}, status=status.HTTP_201_CREATED)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TOTPVerifyView(_OriginAPIView):
    """
    Use this endpoint to verify/enable a TOTP device. Returns True if the code is valid and False otherwise.
    """

    origins = ["web", "app"]
    http_method_names = ["post"]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, token: str, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        user: User = request.user
        device = get_user_totp_device(user)
        if not device == None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            user.validated_2fa()
            return BackendResponse({"response": True}, status=status.HTTP_200_OK)
        return BackendResponse({"response": False}, status=status.HTTP_401_UNAUTHORIZED)


class TOTPDeleteView(GetObjectMixin, _OriginAPIView):
    """
    A view class to delete a TOTP device on pk.
    """

    permission_classes = [IsUserDevice]
    origins = ["app", "web"]
    http_method_names = ["delete"]

    def delete(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().delete(request, format)) is not None:
            return resp
        if not isinstance(pk, int):
            return BackendResponse(
                ["The value of `pk` has to be an integer."],
                status=status.HTTP_400_BAD_REQUEST,
            )
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


class TOTPView(BaseAPIView):
    """
    View class to get a list of the user's TOTP devices.
    """

    origins = ["web", "app"]
    serializer = {"get": GetTOTPSerializer}
    model = TOTPDevice
    get_user_id = True
    http_method_names = ["get"]


class Disable2FA(_OriginAPIView):
    """
    View class to disable 2FA for the user associated with the request.
    """

    origins = ["web", "app"]
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp
        request.user.disable_2fa()
        return BackendResponse(None, status=status.HTTP_204_NO_CONTENT)
