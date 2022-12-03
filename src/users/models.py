from secrets import token_hex
from typing import Any
from knox.models import AuthToken

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from src.users.managers import UserManager
from src.api.models import ProvincesEnum
from src.core.models import TimeStampMixin
from src.core.exceptions import DeletionException


class User(AbstractBaseUser, TimeStampMixin, PermissionsMixin):
    class Roles(models.IntegerChoices):
        GENERATED_USER = 0
        NORMAL_USER = 1
        GARAGE_OWNER = 2
        ADMIN = 3

    first_name = models.CharField(max_length=192, null=True)
    last_name = models.CharField(max_length=192, null=True)
    email = models.EmailField(unique=True)
    role = models.IntegerField(choices=Roles.choices)
    is_active = models.BooleanField(default=True)
    two_factor = models.BooleanField(default=False)
    two_factor_validated = models.BooleanField(null=True, blank=True)
    fav_garage = models.ForeignKey(
        "api.Garage", on_delete=models.CASCADE, null=True, related_name="fav_garage"
    )
    location = models.CharField(max_length=3, choices=ProvincesEnum.choices, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    objects = UserManager()

    def delete(self) -> tuple[int, dict[str, int]]:
        from src.api.models import LicencePlate, Reservation

        if self.is_garage_owner:
            raise DeletionException(
                "You're a garage owner, thus your account cannot be directly deleted. Please contact support if you wish to continue."
            )
        user_lps = LicencePlate.objects.filter(user_id=self.pk)
        for lp in user_lps:
            lp.delete()
        user_reservations = Reservation.objects.filter(user_id=self.pk)
        for reservation in user_reservations:
            reservation.delete()
        user_tokens = AuthToken.objects.filter(user_id=self.pk)
        for token in user_tokens:
            token.delete()
        return super().delete()

    def set_two_factor_validation(self, tf_validated: bool | None) -> None:
        self.two_factor_validated = tf_validated
        self.save()

    @property
    def is_admin(self) -> bool:
        return self.role == 3

    @property
    def is_garage_owner(self) -> bool:
        return self.role == 2

    @property
    def is_normal_user(self) -> bool:
        return self.role == 1

    @property
    def is_generated_user(self) -> bool:
        return self.role == 0

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def email_generator() -> str:
        """
        Generates a random email address.
        """
        return f"{token_hex(8)}@generated.com"
