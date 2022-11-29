from collections import OrderedDict
from typing import Any
from rest_framework import serializers
from src.users.models import User
from django.contrib.auth import authenticate
from src.core.serializers import APIForeignKeySerializer


class UsersSerializer(APIForeignKeySerializer):
    """
    Serializer for serializing GET and PUT request for retrieving and updating the users's data, respectively.
    """

    fav_garage_id = serializers.IntegerField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "first_name",
            "last_name",
            "fav_garage_id",
            "location",
            "two_factor",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"allow_null": True},
            "last_name": {"allow_null": True},
        }


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing sign up POST-requests for creating new users.
    """

    password_confirmation = serializers.CharField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        if data["password"] != data["password_confirmation"]:  # type: ignore
            raise serializers.ValidationError(
                {"errors": ["Password and passwordConfirmation do not match."]}
            )
        return data

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "password_confirmation",
            "role",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "password_confirmation": {"write_only": True},
            "first_name": {"allow_null": True},
            "last_name": {"allow_null": True},
        }


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing the login POST-requests for logging in users.
    """

    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        user = authenticate(**data)
        if user and user.is_active:
            return user  # type: ignore
        raise serializers.ValidationError("Incorrect Credentials Passed.")

    class Meta:
        model = User
        fields = ["email", "password"]
