from rest_framework import serializers

from authentication.services import AuthService


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "ایمیل اجباری است",
            "blank": "ایمیل نمی‌تواند خالی باشد",
        },
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "required": "رمز عبور اجباری است",
            "blank": "رمز عبور نمی‌تواند خالی باشد",
        },
    )

    def validate(self, attrs):
        """
        Validate credentials via AuthService.
        """
        try:
            result = AuthService.login(
                email=attrs["email"],
                password=attrs["password"],
                request=self.context.get("request"),  # type: ignore
            )
        except:
            raise serializers.ValidationError(
                {"email": "ایمیل یا رمز عبور اشتباه است"},
                code="invalid_credentials",
            )

        attrs["auth_result"] = result
        return attrs

    def create(self, validated_data):
        """
        Return login result from service.
        """
        return validated_data["auth_result"]
