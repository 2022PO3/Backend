import json
import datetime
from random import randint
from functools import reduce


def create_fixtures(
    model_name: str,
    fields: list[str],
    values: dict[str, list[str | int | float | None]],
    number: int,
) -> None:
    if not len(set(map(len, values.values()))) == 1:
        raise Exception("Lengths of list values are not equal.")
    values_len = len(list(values.values())[0])
    if "updated_at" in fields:
        values |= {
            "updated_at": [datetime.datetime.now().astimezone().isoformat()]
            * values_len
        }
    if "created_at" in fields:
        values |= {
            "created_at": [datetime.datetime.now().astimezone().isoformat()]
            * values_len
        }

    json_string = json.dumps(
        [
            {
                "model": model_name,
                "pk": i + 1,
                "fields": {field: values[field][i] for field in fields},
            }
            for i in range(values_len)
        ]
    )
    model_name_snake = model_to_snake_case(model_name).replace("api.", "")
    with open(
        f"src/api/seeds/fixtures/00{number}_{model_name_snake}_fixture.json", "w"
    ) as file:
        file.write(json_string)


def model_to_snake_case(model_name: str) -> str:
    """
    Converts the model name in lowerCamelCase to snake_case.
    """
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, model_name).lower()


if __name__ == "__main__":
    create_fixtures(
        "api.garages",
        ["owner", "name", "updated_at", "created_at"],
        {
            "owner": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
            "name": [
                "QPark Hasselt",
                "QPark Leuven",
                "QPark Aalter",
                "QPark Brugge",
                "QPark Herstappe",
                "QPark Oostduinkerke",
                "QPark Antwerpen",
                "QPark Oostende",
                "QPark Mariakerke",
                "QPark Geel",
            ],
        },
        2,
    )
    create_fixtures(
        "api.parkingLots",
        ["garage", "floor_number", "occupied", "created_at", "updated_at"],
        {
            "garage": [randint(1, 10) for _ in range(100)],
            "floor_number": [randint(-2, 2) for _ in range(100)],
            "occupied": [randint(0, 1) for _ in range(100)],
        },
        3,
    )
    create_fixtures(
        "api.licencePlates",
        ["user", "licence_plate", "garage", "created_at", "updated_at"],
        {
            "user": [1, 1, 2, 2, 3, 4, 5],
            "licence_plate": [
                "1ABC123",
                "2JIO489",
                "1JFK908",
                "8FJO108",
                "2AZP367",
                "1KPX789",
                "1FKO392",
            ],
            "garage": [1, None, 3, 4, 5, None, None],
        },
        4,
    )
    create_fixtures(
        "api.locations",
        [
            "garage_id",
            "country",
            "province",
            "municipality",
            "post_code",
            "street",
            "number",
            "updated_at",
            "created_at",
        ],
        {
            "garage_id": [1, 2],
            "country": ["België"] * 2,
            "province": ["LIM"] * 2,
            "municipality": ["Hasselt", "Lummen"],
            "post_code": [3500, 3000],
            "street": ["Toekomststraat", "Sint-Annastraat"],
            "number": [43, 590],
        },
        5,
    )
    create_fixtures(
        "api.garageSettings",
        [
            "garage_id",
            "max_height",
            "location",
            "max_width",
            "max_handicapped_lots",
            "created_at",
            "updated_at",
        ],
        {
            "garage_id": [1, 2],
            "max_height": [1.9, 2.1],
            "location": [1, 2],
            "max_width": [1.8, 1.95],
            "max_handicapped_lots": [10, 12],
        },
        6,
    )
