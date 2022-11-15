from secrets import token_hex
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from src.users.managers import UserManager
from src.core.models import TimeStampMixin


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
    settings_id = models.ForeignKey("api.Settings", on_delete=models.CASCADE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    objects = UserManager()

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
