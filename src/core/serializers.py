from rest_framework import serializers
from django.db.models import Model


from typing import TypeVar

T = TypeVar("T", bound=Model)


class Meta:
    def __new__(cls, model_name: T, fields: list[str] | str, *args, **kwargs):
        setattr(cls, "model", model_name)
        setattr(cls, "fields", fields)
        return super().__new__(cls, *args, **kwargs)


class APIBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer class from which all serializers for API models should inherit from. It
    converts all field from snake_case to lowerCamelCase with the correct source attribute.
    """

    model: T  # type: ignore
    # field_names: list[str] | str

    def __new__(cls, *args, **kwargs):
        camel_case_fields = cls.to_lower_camel_case(cls.get_fields_tuple())
        cls.create_fields(camel_case_fields)
        cls.create_meta_class()
        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def get_fields_tuple(cls) -> list[tuple[str, str]]:
        """
        Returns a tuple of length 2 where the first element represents the field class name and
        the second element the name of the field.
        """
        return list(
            map(lambda x: (x.get_internal_type(), x.name), cls.model._meta.fields)
        )

    @classmethod
    def to_lower_camel_case(
        cls, field_names: list[tuple[str, str]]
    ) -> list[tuple[str, str, str]]:
        def to_camel_case(field_tuple: tuple[str, str]) -> tuple[str, str, str]:
            """
            Returns a tuple of length 3 where the first element represents the field class name,
            the second the field name in snake_case and the last one the field name in
            lowerCamelCase.
            """
            if field_tuple[0] == "ForeignKey":
                field_tuple = ("IntegerField", f"{field_tuple[1]}_id")
            components = field_tuple[1].split("_")
            return (
                field_tuple[0],
                field_tuple[1],
                components[0] + "".join(x.title() for x in components[1:]),
            )

        return list(map(to_camel_case, field_names))

    @classmethod
    def create_fields(cls, camel_case_fields: list[tuple[str, str, str]]) -> None:
        """
        Creates the fields with the correct name and source attribute.
        """
        for field_tuple in camel_case_fields:
            if "_" in field_tuple[1]:
                print("class", cls)
                setattr(
                    cls,
                    field_tuple[2],
                    eval(f"serializers.{field_tuple[0]}")(source=field_tuple[1]),
                )

    @classmethod
    def create_meta_class(cls) -> None:
        setattr(cls, "Meta", Meta(cls.model, cls.field_names))
