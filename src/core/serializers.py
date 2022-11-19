from rest_framework.serializers import BaseSerializer
from django.db.models import Model


from typing import TypeVar, Any

T = TypeVar("T", bound=Model)


class APIBaseSerializer(BaseSerializer):
    model: T  # type: ignore

    def get_fields_name(self) -> list[tuple[str, str]]:
        return list(map(lambda x: x.name, self.model._meta.fields))

    def to_lower_camel_case(self, field_name: list[str]) -> list[str]:
        def to_camel_case(snake_str: str) -> str:
            components = snake_str.split("_")
            return components[0] + "".join(x.title() for x in components[1:])

        return list(map(to_camel_case, field_name))
    
    def create_fields(self, camel_case_fields: list[str]) -> None:
        pass

    class Meta:
        pass
