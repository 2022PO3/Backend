import os

from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from src.core.views import BackendResponse


class ValidateOrigin:
    """
    Class to implement origin validation for API views.
    """

    BASE_ORIGINS = ["rpi", "app", "web"]

    origins = []

    def _validate_origins(self, request: Request) -> None:
        """
        Checks if the given origin(s) in the request are valid, based on the `BASE_ORIGINS` and
        on the custom-defined `origins` and validates the sent case in case of the Raspberry Pi
        and the frontend application.
        """

        try:
            origin: str = request.headers["PO3-ORIGIN"]
        except KeyError:
            raise OriginValidationException(
                "The PO3-ORIGIN-header is not sent with the request.",
                status.HTTP_400_BAD_REQUEST,
            )
        if origin not in self.BASE_ORIGINS:
            raise OriginValidationException(
                "The PO3-ORIGIN-header contains a wrong value. It can only be `rpi`, `app` or `web`.",
                status.HTTP_400_BAD_REQUEST,
            )
        elif origin not in self.origins:
            raise OriginValidationException(
                f"The origin `{origin}` is not allowed on this view.",
                status.HTTP_403_FORBIDDEN,
            )
        elif origin == "rpi":
            self._validate_key(
                request, "PO3-RPI-KEY", "HASHED_RASPBERRY_PI_KEY", "Raspberry Pi"
            )
        elif origin == "app" or origin == "web":
            self._validate_key(
                request, "PO3-APP-KEY", "HASHED_APP_KEY", "frontend application"
            )

    def _validate_key(
        self, request: Request, header_name: str, env_name: str, origin_name: str
    ) -> None:
        """
        Validates the sent key with the header `header_name` and checks if it matches the
        hashed key in `env_name`. It throws the correct error in case of failures.
        """

        try:
            sent_key: str = request.headers[header_name]
        except KeyError:
            raise OriginValidationException(
                f"The secret key of the {origin_name} is not sent.",
                status.HTTP_400_BAD_REQUEST,
            )
        else:
            hashed_pi_key = os.environ[env_name]
            if hashed_pi_key is None:
                raise OriginValidationException(
                    "Cannot validate the secret key, as none is installed on the server.",
                    status.HTTP_400_BAD_REQUEST,
                )
            if not check_password(sent_key, hashed_pi_key):
                raise OriginValidationException(
                    f"Validation of the secret key of the {origin_name} failed.",
                    status.HTTP_403_FORBIDDEN,
                )


class OriginAPIView(ValidateOrigin, APIView):
    """
    Class which implements the origin validation for the API views. The `get`, `post`, `put` and `delete`-methods are defined such that they validate the origin of the request based on the `origins`-list.

    In order to extend one of the request-types, use the following code in the child-class::

        if (resp := super().request_name(request, format)) is not None:
            return resp
    """

    origins: list[str] = []

    def get(self, request: Request, format=None) -> BackendResponse | None:
        return self._validate_origins(request)

    def post(self, request: Request, format=None) -> BackendResponse | None:
        return self._validate_origins(request)

    def put(self, request: Request, format=None) -> BackendResponse | None:
        return self._validate_origins(request)

    def delete(self, request: Request, format=None) -> BackendResponse | None:
        return self._validate_origins(request)

    def _validate_origins(self, request: Request) -> None | BackendResponse:
        try:
            super()._validate_origins(request)
        except OriginValidationException as e:
            return BackendResponse([str(e)], status=e.status)


class OriginValidationException(Exception):
    """
    Exception raised when there is an error in the origin validation of the request.
    """

    def __init__(self, message: str, status_code: int) -> None:
        self.status = status_code
        super().__init__(message)
