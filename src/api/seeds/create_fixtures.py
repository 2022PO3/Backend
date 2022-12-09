import json
import datetime
from faker import Faker
from random import randint, uniform, choice, choices
from functools import reduce


def create_fixtures(
    model_name: str,
    fields: list[str],
    values: dict[str, list],
    number: int,
) -> None:
    if not len(set(map(len, values.values()))) == 1:
        raise Exception(f"Lengths of list values of {number} are not equal.")
    values_len = len(list(values.values())[0])
    if "created_at" in fields:
        values |= {
            "created_at": [
                datetime.datetime.now().astimezone().isoformat()
                for _ in range(values_len)
            ]
        }
    if "updated_at" in fields:
        values |= {
            "updated_at": [
                datetime.datetime.now().astimezone().isoformat()
                for _ in range(values_len)
            ]
        }

    json_string = json.dumps(
        [
            {
                "model": model_name,
                "pk": i + 1,
                "fields": {field: values[field][i] for field in fields},
            }
            for i in range(values_len)
        ],
        indent=4,
    )
    model_name_snake = model_to_snake_case(model_name).replace("api.", "")
    no = f"000{number}" if number < 10 else f"00{number}"
    with open(
        f"src/api/seeds/fixtures/{no}_{model_name_snake}_fixture.json", "w"
    ) as file:
        file.write(json_string)


def model_to_snake_case(model_name: str) -> str:
    """
    Converts the model name in lowerCamelCase to snake_case.
    """
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, model_name).lower()


if __name__ == "__main__":
    faker = Faker(["nl-BE"])
    cities = [faker.city() for _ in range(10)] + ["Leuven"]
    create_fixtures(
        "api.location",
        [
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
            "country": ["België"] * 11,
            "province": [choice(["LIM", "ANT", "WVL", "OVL", "VBR"]) for _ in range(10)]
            + ["VBR"],
            "municipality": cities,
            "post_code": [randint(2000, 4000) for _ in range(10)] + [3000],
            "street": [faker.street_name() for _ in range(10)] + ["Celestijnenlaan"],
            "number": [randint(2, 200) for _ in range(10)] + [200],
        },
        2,
    )
    create_fixtures(
        "api.garageSettings",
        [
            "max_height",
            "location",
            "electric_cars",
            "max_width",
            "max_handicapped_lots",
            "created_at",
            "updated_at",
        ],
        {
            "electric_cars": [randint(2, 10) for _ in range(10)],
            "max_height": [round(uniform(1.8, 2.4), 1) for _ in range(10)],
            "location": [i for i in range(1, 11)],
            "max_width": [round(uniform(1.8, 2.4), 1) for _ in range(10)],
            "max_handicapped_lots": [randint(2, 10) for _ in range(10)],
        },
        3,
    )
    create_fixtures(
        "api.garage",
        ["user", "name", "garage_settings", "updated_at", "created_at"],
        {
            "user": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 3],
            "name": list(map(lambda city: f"QPark {city}", cities)),
            "garage_settings": [i for i in range(1, 11)] + [11],
        },
        4,
    )
    create_fixtures(
        "api.parkingLot",
        [
            "garage",
            "floor_number",
            "occupied",
            "disabled",
            "created_at",
            "updated_at",
            "parking_lot_no",
        ],
        {
            "garage": list(map(lambda x: x // 30 + 1, list(range(300)))) + [11] * 6,
            "floor_number": [randint(-2, 2) for _ in range(300)] + [0] * 6,
            "occupied": [randint(0, 1) for _ in range(300)] + [0] * 6,
            "disabled": [choices([0, 1], [0.95, 0.05])[0] for _ in range(300)]
            + [0] * 6,
            "parking_lot_no": list(map(lambda x: x % 30 + 1, list(range(300))))
            + list(range(1, 7)),
        },
        5,
    )
    create_fixtures(
        "api.licencePlate",
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
            "garage": [2, None, 3, 4, 5, None, None],
        },
        6,
    )
    create_fixtures(
        "api.price",
        [
            "garage",
            "price_string",
            "duration",
            "price",
            "valuta",
            "created_at",
            "updated_at",
        ],
        {
            "garage": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10],
            "price_string": [f"{randint(1, 10)} uur parkeren" for _ in range(20)],
            "duration": [
                str(datetime.timedelta(hours=1)),
                str(datetime.timedelta(minutes=15)),
            ]
            * 10,
            "price": [round(uniform(4.0, 15.0), 1) for _ in range(20)],
            "valuta": ["EUR"] * 20,
        },
        7,
    )
    create_fixtures(
        "api.openingHour",
        [
            "garage",
            "from_day",
            "to_day",
            "from_hour",
            "to_hour",
            "updated_at",
            "created_at",
        ],
        {
            "garage": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10],
            "from_day": [0, 6] * 10,
            "to_day": [5, 6] * 10,
            "from_hour": [str(datetime.time(0, 0, 0)), str(datetime.time(5, 0, 0))]
            * 10,
            "to_hour": [str(datetime.time(23, 59, 0)), str(datetime.time(22, 0, 0))]
            * 10,
        },
        8,
    )
    create_fixtures(
        "api.reservation",
        [
            "garage",
            "user",
            "licence_plate",
            "parking_lot",
            "from_date",
            "to_date",
            "updated_at",
            "created_at",
        ],
        {
            "garage": [randint(1, 10) for _ in range(10)],
            "user": [1, 1, 2, 2, 3, 4, 5, 1, 1, 2],
            "licence_plate": [1, 2, 3, 4, 5, 6, 7, 1, 2, 3],
            "parking_lot": [randint(1, 100) for _ in range(10)],
            "from_date": [
                datetime.datetime(2022, 12, randint(20, 21), randint(0, 12))
                .astimezone()
                .isoformat()
                for _ in range(10)
            ],
            "to_date": [
                datetime.datetime(2022, 12, randint(21, 22), randint(13, 23))
                .astimezone()
                .isoformat()
                for _ in range(10)
            ],
        },
        9,
    )
