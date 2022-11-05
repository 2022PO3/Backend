from rest_framework import serializers
from src.users.models import User
from django.contrib.auth import authenticate


class UsersSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")

    class Meta:
        model = User
        fields = ["id", "email", "role", "firstName", "lastName"]
        extra_kwargs = {"password": {"write_only": True}}


class SignUpSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")

    class Meta:
        model = User
        field = ["id", "email", "password", "role", "firstName", "lastName"]
        extra_kwargs = {"password": {"write_only": True}}


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
