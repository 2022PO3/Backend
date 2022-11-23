from functools import reduce


def to_snake_case(string: str) -> str:
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, string).lower()


def to_camel_case(string: str, *, lower_case: bool = True) -> str:
    init, *temp = string.split("_")
    lower_camel_case = "".join([init.lower(), *map(str.title, temp)])
    return (
        lower_camel_case
        if lower_case
        else lower_camel_case[0].capitalize() + lower_camel_case[1:]
    )
