from django.http import Http404, JsonResponse

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from typing import TypeVar, Any


T = TypeVar("T")


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
        data: str | list[str] | dict[str, Any] | None, status: int | None
    ) -> dict | None:
        if data is None or status is None:
            return None
        return {"errors": data} if status >= 400 else {"data": data}

    @staticmethod
    def __set_content_type(content_type: str | None) -> str | None:
        return "application/json" if content_type is None else content_type

    # TODO Add default headers for the Backend.


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
