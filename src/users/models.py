from random import choices
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from src.users.managers import UserManager
from src.core.models import TimeStampMixin


class User(AbstractBaseUser, TimeStampMixin, PermissionsMixin):
    class Roles(models.IntegerChoices):
        NORMAL_USER = 1
        GARAGE_OWNER = 2
        ADMIN = 3

    first_name = models.CharField(max_length=192)
    last_name = models.CharField(max_length=192)
    email = models.EmailField(unique=True)
    role = models.IntegerField(choices=Roles.choices)
    is_active = models.BooleanField(default=True)
    license_plate = models.CharField(max_length=192)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["licence_plate", "role"]

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
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
