from collections import OrderedDict
import os
import json

from typing import Callable, TypeVar, Any

from django.db import models
from django.http import Http404, JsonResponse
from django.contrib.auth.hashers import check_password
from jwt.exceptions import DecodeError, ExpiredSignatureError

from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from src.core.utils import to_camel_case, to_snake_case, decode_jwt
from src.core.exceptions import BackendException
from src.core.utils import to_camel_case, to_snake_case
from src.core.exceptions import OriginValidationException, DeletionException

T = TypeVar("T")
U = TypeVar("U", bound=serializers.ModelSerializer)
V = TypeVar("V", bound=models.Model)


class BackendResponse(Response):
    """
    Extended `Response`-class of the Django Rest Framework, which adds default headers and content-type. Furthermore, it adds a top level key to the JSON-output: `data` if the status code indicates success and `errors` if the status code indicates an error.
    """

    def __init__(
        self,
        data: list[str] | dict[str, Any] | None = None,
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
        data: list[str] | dict[str, Any] | None,
        status: int | None,
    ) -> dict | None:
        print(data)
        if data is None or status is None:
            return None
        return (
            {"errors": BackendResponse.__handle_error_data(data)}
            if status >= 400
            else {
                "data": BackendResponse.__escape_data(
                    _dict_key_to_case(data, to_camel_case)
                )
                if isinstance(data, dict)
                else list(map(lambda d: BackendResponse.__escape_data(_dict_key_to_case(d, to_camel_case)), data))  # type: ignore
            }
        )

    @staticmethod
    def __escape_data(data: str | list[str] | dict[str, Any]):
        """
        Escapes given data to be safely transmitted via the API. This means that special characters, like accents are escaped.
        """
        if isinstance(data, str):
            return BackendResponse.__escape_string(data)
        elif isinstance(data, list):
            return [BackendResponse.__escape_data(d) for d in data]
        elif isinstance(data, OrderedDict) or isinstance(data, dict):
            escaped_data = {}
            for k, v in data.items():
                if isinstance(v, OrderedDict):
                    escaped_data |= {k: BackendResponse.__escape_data(v)}
                elif isinstance(v, str):
                    escaped_data |= {k: BackendResponse.__escape_string(v)}
                else:
                    escaped_data |= {k: v}
            return escaped_data

    @staticmethod
    def __escape_string(string: str) -> str:
        return json.dumps(string).replace('"', "")

    @staticmethod
    def __set_content_type(content_type: str | None) -> str | None:
        return "application/json" if content_type is None else content_type

    @staticmethod
    def __handle_error_data(data: list[str] | dict[str, Any]) -> list[str]:
        if isinstance(data, list):
            return data
        else:
            errors: list[str] = []
            for key in data.keys():
                if isinstance(data[key], list):
                    errors.append(f"{key}: {data[key][0].lower()}")
                else:
                    errors.append(data[key])
            return errors


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
            encoded_jwt: str = request.headers[header_name]
        except KeyError:
            raise OriginValidationException(
                f"The secret key of the {origin_name} is not sent.",
                status.HTTP_400_BAD_REQUEST,
            )
        try:
            decoded_data = decode_jwt(encoded_jwt, "JWT_SECRET")
        except (ExpiredSignatureError, DecodeError, BackendException) as e:
            raise OriginValidationException(
                f"{e.__class__.__name__}: {str(e)}",
                status.HTTP_403_FORBIDDEN,
            )
        hashed_pi_key = os.environ[env_name].replace("\\", "")
        if hashed_pi_key is None:
            raise OriginValidationException(
                "Cannot validate the secret key, as none is installed on the server.",
                status.HTTP_400_BAD_REQUEST,
            )
        if not check_password(decoded_data["key"], hashed_pi_key):
            raise OriginValidationException(
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
    renderer_classes = [JSONRenderer]

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
    serializer: dict[str, U] = None  # type: ignore
    model: V = None  # type: ignore
    get_user_id = False
    post_user_id = False

    def get(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        if self.model and not self.get_user_id:
            objects = self.model.objects.all()  # type: ignore
            serializer = self.serializer["get"](objects, many=True)  # type: ignore
        else:
            objects = self.model.objects.filter(**{"user_id": request.user.pk})  # type: ignore
            serializer = self.serializer["get"](objects, many=True)  # type: ignore
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None) -> BackendResponse | None:
        if (resp := super().post(request, format)) is not None:
            return resp
        data = _dict_key_to_case(JSONParser().parse(request), to_snake_case)
        serializer = self.serializer["post"](data=data)  # type: ignore
        if serializer.is_valid():
            try:
                self.check_object_permissions(
                    request, serializer.validated_data["garage_id"]
                )
            except KeyError:
                pass
            serializer.save(
                user=request.user
            ) if self.post_user_id else serializer.save()
            return BackendResponse(serializer.data, status=status.HTTP_201_CREATED)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PkAPIView(_OriginAPIView, GetObjectMixin):
    model: V = None  # type: ignore
    fk_model = None  # type: ignore
    serializer: U = None  # type: ignore
    list = False
    column: str = ""
    user_id = False

    def get(
        self, request: Request, pk: int | None = None, format=None
    ) -> BackendResponse:
        if (resp := super().get(request, format)) is not None:
            return resp
        try:
            if pk is None:
                # Special case for the UserView
                data = request.user  # type: ignore
            elif self.list:
                data: list[V] = self.model.objects.filter(**{self.column: pk})  # type: ignore
            elif self.fk_model is None:
                data: V = self.get_object(self.model, pk)  # type: ignore
            else:
                data: V = getattr(self.get_object(self.fk_model, pk), to_snake_case(self.model.__name__))  # type: ignore
        except Http404:
            return BackendResponse(
                [
                    f"The corresponding {self.fk_model.__name__ if self.fk_model else self.model.__name__} with 'pk' `{pk}` does not exist."  # type: ignore
                ],
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer: U = self.serializer(data, many=self.list)  # type: ignore
        return BackendResponse(serializer.data, status=status.HTTP_200_OK)

    def put(
        self, request: Request, pk: int | None = None, format=None
    ) -> BackendResponse:
        if (resp := super().put(request, format)) is not None:
            return resp
        data = _dict_key_to_case(JSONParser().parse(request), to_snake_case)
        # For the UserView, no model has to be defined.
        if self.model is not None:
            try:
                object = self.get_object(self.model, pk)  # type: ignore
            except Http404:
                return BackendResponse(
                    [f"The {self.model.__name__} with pk `{pk}` does not exist,"],  # type: ignore
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = self.serializer(object, data=data)  # type: ignore
        else:
            # Special case for the UserView.
            serializer = self.serializer(request.user, data=data)  # type: ignore
        if serializer.is_valid():
            try:
                self.check_object_permissions(
                    request, serializer.validated_data["garage_id"]
                )
            except KeyError:
                # When the object is a Garage.
                self.check_object_permissions(request, pk)
            serializer.save(user=request.user) if self.user_id else serializer.save()
            return BackendResponse(serializer.data, status=status.HTTP_200_OK)
        return BackendResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(
        self, request: Request, pk: int | None = None, format=None
    ) -> BackendResponse | None:
        try:
            if pk is None:
                data = request.user  # type: ignore
            else:
                data: V = self.get_object(self.model, pk)  # type: ignore
        except Http404:
            return BackendResponse(
                [
                    f"The corresponding {self.model.__name__} with 'pk' `{pk}` does not exist."  # type: ignore
                ],
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            print(data)
            data.delete()
        except DeletionException as e:
            return BackendResponse([str(e)], status=status.HTTP_400_BAD_REQUEST)
        return BackendResponse(None, status=status.HTTP_204_NO_CONTENT)


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
