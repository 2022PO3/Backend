from __future__ import annotations
from typing import TYPE_CHECKING
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password

if TYPE_CHECKING:
    from src.users.models import User


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(
        self,
        email,
        password,
        role,
        *,
        is_active=False,
        **extra_fields,
    ) -> User:
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, is_active=is_active, **extra_fields)
        validate_password(password)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields) -> User:
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)
