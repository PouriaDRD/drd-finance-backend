from rest_framework import serializers

from finance.enums import CategoryType
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


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating category.
    """

    name = serializers.CharField(
        help_text="Category name (e.g., Food, Salary, Rent)",
        min_length=3,
        max_length=256,
        required=True,
        error_messages={
            "required": "نام دسته بندی الزامی است.",
            "min_length": "نام دسته بندی باید حداقل 3 کاراکتر داشته باشد.",
            "max_length": "نام دسته بندی بیشتر از 256 کاراکتر است.",
        },
    )

    type = serializers.ChoiceField(choices=CategoryType.choices)

    is_archived = serializers.BooleanField(default=False)

    class Meta:
        model = CategoryModel

        fields = (
            "name",
            "type",
            "is_archived",
            # "icon",
            # "color",
        )

    def validate_name(self, value):
        return value.strip()

    # def validate_color(self, value):
    #     if not value.startswith("#"):
    #         raise serializers.ValidationError("Color must be HEX format.")

    #     if len(value) != 7:
    #         raise serializers.ValidationError("Invalid HEX color.")

    #     return value
