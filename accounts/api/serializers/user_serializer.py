from rest_framework import serializers

from accounts.models import UserModel


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for UserModel.
    """

    class Meta:
        model = UserModel

        fields = (
            "id",
            "email",
            "email_verified",
            "name",
            "role",
            "status",
            "last_login",
            "created_at",
        )

        read_only_fields = [
            "__all__",
        ]
