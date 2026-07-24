from rest_framework import serializers
from django.core.validators import EmailValidator

from authentication.services import AuthService


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for registering a user.
    """

    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator],
        error_messages={
            "required": "ایمیل اجباری است",
            "blank": "ایمیل نمی تواند خالی باشد",
        },
    )

    name = serializers.CharField(
        required=True,
        min_length=3,
        max_length=255,
        error_messages={
            "required": "نام اجباری است",
            "blank": "نام نمی تواند خالی باشد",
            "min_length": "نام باید حداقل 3 کاراکتر داشته باشد",
            "max_length": "نام باید حداکثر 255 کاراکتر داشته باشد",
        },
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "required": "رمز عبور اجباری است",
            "blank": "رمز عبور نمی تواند خالی باشد",
        },
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "required": "تایید رمز عبور اجباری است",
            "blank": "تایی عبور نمی تواند خالی باشد",
        },
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "رمز عبور مطابقت ندارد."}
            )

        attrs.pop("confirm_password")

        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        name = validated_data["name"]
        password = validated_data["password"]
        request = self.context.get("request")

        result = AuthService.register(
            name=name,
            email=email,
            password=password,
            request=request,  # type: ignore
        )

        return result
