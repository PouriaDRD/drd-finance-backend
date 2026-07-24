from rest_framework import serializers

from authentication.models import LoginHistoryModel


class LoginHistorySerializer(serializers.ModelSerializer):

    class Meta:

        model = LoginHistoryModel

        fields = (
            "id",
            "ip_address",
            "user_agent",
            "device",
            "browser",
            "operating_system",
            "country",
            "city",
            "is_successful",
            "failure_reason",
            "created_at",
        )
        read_only_fields = ["__all__"]
