import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharacterValidation:
    """
    Password validator which checks if the given password contains at least 1 special
    character (by default). It can be extended to check for multiple special characters.
    """

    def __init__(self, special_chars: int = 1):
        self.special_chars = special_chars

    def validate(self, password: str, user=None) -> None:
        SPECIAL_CHARACTER_REGEX = r"[@_!#$%^&*()<>?/\|}{~:;]"

        if len(re.findall(SPECIAL_CHARACTER_REGEX, password)) < self.special_chars:
            raise ValidationError(
                _(
                    f"This password must contain at least {self.special_chars}  special character(s)."
                ),
                code="no_special_characters",
            )

    def get_help_text(self):
        return _(
            f"Your password must contain at least {self.special_chars} special character(s)."
        )


class MinimumNumberValidation:
    """
    Password validator which checks if the given password contains at least 1 numerical
    character (by default). It can be extended to check for multiple numerical characters.
    """

    def __init__(self, number_chars: int = 1):
        self.number_chars = number_chars

    def validate(self, password: str, user=None) -> None:
        NUMBER_REGEX = r"\d"

        if len(re.findall(NUMBER_REGEX, password)) < self.number_chars:
            raise ValidationError(
                _(
                    f"This password must contain at least {self.number_chars}  numerical character(s)."
                ),
                code="no_numerical_characters",
            )

    def get_help_text(self):
        return _(
            f"Your password must contain at least {self.number_chars} numerical character(s)."
        )
