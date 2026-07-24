from rest_framework import serializers

from finance.models import CategoryModel


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel

        fields = (
            "id",
            "name",
            "type",
            # "icon",
            # "color",
            "is_archived",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "name",
            "type",
            # "icon",
            # "color",
            "is_archived",
            "created_at",
            "updated_at",
        )
