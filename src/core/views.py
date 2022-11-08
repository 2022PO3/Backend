from django.http import Http404

from rest_framework.response import Response

from typing import TypeVar, Any

T = TypeVar("T")


class GetObjectMixin:
    def get_object(self, cls: T, pk: int) -> T:
        """
        Retrieves the `T`-object with the given `pk` from the database.
        """
        try:
            return cls.objects.get(pk=pk)  # type: ignore
        except cls.DoesNotExist:  # type: ignore
            raise Http404


class BackendResponse(Response):
    """
    Extended `Response`-class of the Django Rest Framework, which adds default headers and content-type. Furthermore, it adds a top level key to the JSON-output: `data` if the status code indicates success and `errors` if the status code indicates an error.
    """

    def __init__(
        self,
        data: str | list[str] | dict[str, Any] | None = None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        super().__init__(
            data=BackendResponse.__assign_top_level_key(data, status),
            status=None,
            template_name=None,
            headers=None,
            exception=False,
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
