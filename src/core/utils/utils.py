import jwt

from typing import Any
from functools import reduce
from os import path, getenv
from dotenv import load_dotenv

from src.core.exceptions import BackendException


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


def decode_jwt(
    encoded_jwt: str, secret_env_name: str, algorithm="HS256"
) -> dict[str, Any]:
    """
    Helper function to decode JWT-tokens coming from the Frontend application.
    """
    # Load the `.env`-file.
    dotenv_path = path.abspath(".env")
    load_dotenv(dotenv_path)
    if (secret := getenv(secret_env_name)) is None:
        raise BackendException("No secret key present for decoding the JWT-token.")
    return jwt.decode(encoded_jwt, secret, algorithms=[algorithm], leeway=5)
