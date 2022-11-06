from django.db import models
from django.http import Http404

from typing import TypeVar

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
