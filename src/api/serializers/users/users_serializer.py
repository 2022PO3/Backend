from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from src.users.models import User
from django.contrib.auth import authenticate


class UsersSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    favGarageId = serializers.IntegerField(source="fav_garage")

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "firstName",
            "lastName",
            "favGarageId",
            "location",
        ]
        extra_kwargs = {"password": {"write_only": True}}


class SignUpSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source="first_name", allow_null=True)
    lastName = serializers.CharField(source="last_name", allow_null=True)
    passwordConfirmation = serializers.CharField(max_length=192, write_only=True)

    def is_valid(self, raise_exception: bool = False) -> bool:
        if "firstName" not in self.initial_data:  # type: ignore
            self.initial_data |= {"firstName": None}  # type: ignore
        if "lastName" not in self.initial_data:  # type: ignore
            self.initial_data |= {"lastName": None}  # type: ignore
        if not super().is_valid():
            return False
        if self.initial_data["password"] != self.initial_data["passwordConfirmation"]:  # type: ignore
            raise ValidationError(
                {"errors": ["Password and passwordConfirmation do not match."]}
            )
        return True

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "passwordConfirmation",
            "role",
            "firstName",
            "lastName",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials Passed.")

    class Meta:
        model = User
        fields = ["email", "password"]