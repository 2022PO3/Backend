import os
import re
from functools import reduce
from typing import Callable, TypeVar, Any

from django.db import models
from django.http import Http404, JsonResponse
from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response

from src.core.utils import to_camel_case, to_snake_case

T = TypeVar("T")
U = TypeVar("U", bound=serializers.ModelSerializer)
V = TypeVar("V", bound=models.Model)


class BackendResponse(Response):
    """
    Extended `Response`-class of the Django Rest Framework, which adds default headers and content-type. Furthermore, it adds a top level key to the JSON-output: `data` if the status code indicates success and `errors` if the status code indicates an error.
    """

    def __init__(
        self,
        data: str | list[str] | dict[str, Any] | None = None,
        status: int | None = None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        super().__init__(
            data=BackendResponse.__assign_top_level_key(data, status),
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=BackendResponse.__set_content_type(content_type),
        )

    @staticmethod
    def __assign_top_level_key(
        data: str | list[str] | dict[str, Any] | None | list[dict[str, Any]],
        status: int | None,
    ) -> dict | None:
        if data is None or status is None:
            return None
        return (
            {"errors": data}
            if status >= 400
            else {
                "data": _dict_key_to_case(data, to_camel_case)
                if isinstance(data, dict)
                else list(map(lambda d: _dict_key_to_case(d, to_camel_case), data))  # type: ignore
            }
        )

    @staticmethod
    def __set_content_type(content_type: str | None) -> str | None:
        return "application/json" if content_type is None else content_type


class _ValidateOrigin:
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
            raise _OriginValidationException(
                "The PO3-ORIGIN-header is not sent with the request.",
                status.HTTP_400_BAD_REQUEST,
            )
        if origin not in self.BASE_ORIGINS:
            raise _OriginValidationException(
                "The PO3-ORIGIN-header contains a wrong value. It can only be `rpi`, `app` or `web`.",
                status.HTTP_400_BAD_REQUEST,
            )
        elif origin not in self.origins:
            raise _OriginValidationException(
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
            raise _OriginValidationException(
                "The secret key of the frontend application is not sent.",
                status.HTTP_400_BAD_REQUEST,
            )
        else:
            hashed_pi_key = os.environ[env_name]
            if hashed_pi_key is None:
                raise _OriginValidationException(
                    "Cannot validate the secret key, as none is installed on the server.",
                    status.HTTP_400_BAD_REQUEST,
                )
            if not check_password(sent_key, hashed_pi_key):
                raise _OriginValidationException(
                    f"Validation of the secret key of the {origin_name} failed.",
                    status.HTTP_403_FORBIDDEN,
                )


class _OriginAPIView(_ValidateOrigin, APIView):
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
        except _OriginValidationException as e:
            return BackendResponse([str(e)], status=e.status)


class _OriginValidationException(Exception):
    """
    Exception raised when there is an error in the origin validation of the request.
    """

    def __init__(self, message: str, status_code: int) -> None:
        self.status = status_code
        super().__init__(message)


class GetObjectMixin:
    def get_object(self, cls: T, pk: int) -> T:
        """
        Retrieves the `T`-object with the given `pk` from the database.
        """
        try:
            return cls.objects.get(pk=pk)  # type: ignore
        except cls.DoesNotExist:  # type: ignore
            raise Http404

    def get_object_on_field(self, cls: T, field_name: str, field_value: str | int) -> T:
        """
        Retrieves the `T`-object with the given `field_value` for `field_name` from the database.
        """
        try:
            return cls.objects.get(**{field_name: field_value})  # type: ignore
        except cls.DoesNotExist:  # type: ignore
            raise Http404


class BaseAPIView(_OriginAPIView, GetObjectMixin):
    serializer: U = None  # type: ignore
    model: V = None  # type: ignore
    user_id = False

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        if self.model and not self.user_id:
            objects = self.model.objects.all()  # type: ignore
            serializer = self.serializer(objects, many=True)  # type: ignore
        elif self.user_id:
            objects = self.model.objects.filter(**{"user_id": request.user.pk})  # type: ignore
            serializer = self.serializer(objects, many=True)  # type: ignore
        else:
            serializer = self.serializer(request.user)  # type: ignore
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp
        data = _dict_key_to_case(JSONParser().parse(request), to_snake_case)
        serializer = self.serializer(data=data)  # type: ignore
        if serializer.is_valid():
            try:
                self.check_object_permissions(
                    request, serializer.validated_data["garage_id"]
                )
            except KeyError:
                pass
            serializer.save(user=request.user) if self.user_id else serializer.save()
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(
        self, request: Request, pk: int | None = None, format=None
    ) -> BackendResponse:
        if (resp := super().put(request, format)) is not None:
            return resp
        data = _dict_key_to_case(JSONParser().parse(request), to_snake_case)
        if self.model is not None:
            try:
                object = self.get_object(self.model, pk)
            except Http404:
                return BackendResponse(
                    [f"The {self.model} with pk `{pk}` does not exist,"],
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = self.serializer(object, data=data)  # type: ignore
        else:
            serializer = self.serializer(request.user, data=data)  # type: ignore
        print(serializer.initial_data)
        if serializer.is_valid():
            try:
                self.check_object_permissions(
                    request, serializer.validated_data["garage_id"]
                )
                pass
            except KeyError:
                pass
            serializer.save(user=request.user) if self.user_id else serializer.save()
            print(serializer.data)
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PkAPIView(_OriginAPIView, GetObjectMixin):
    model: V = None  # type: ignore
    column: str = None  # type: ignore
    serializer: U = None  # type: ignore
    list = False

    def get(self, request: Request, pk: int, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            if self.column is None:
                data: V = self.model.get_object(self.model, pk)  # type: ignore
            elif self.list:
                data: list[V] = self.model.objects.filter(**{self.column: pk})  # type: ignore
            else:
                data: V = self.model.get_object_on_field(self.model, self.column, pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [
                    f"The corresponding {self.model} with {self.column if not self.column else 'pk'} `{pk}` does not exist."
                ],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: U = self.serializer(data, many=self.list)  # type: ignore
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)


def _dict_key_to_case(d: dict[str, Any], f: Callable) -> dict[str, Any]:
    d_copy = d.copy()
    for key in d.keys():
        case_key = f(key)
        if isinstance(d_copy[key], dict):
            d_copy[case_key] = _dict_key_to_case(d_copy.pop(key), f)
        else:
            d_copy[case_key] = d_copy.pop(key)
    return d_copy


def server_error(request: Request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    data = {
        "errors": [
            "There happened an exception on the server, which caused the request to fail."
        ]
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
