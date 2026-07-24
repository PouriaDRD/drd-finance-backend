from django.db import transaction
from rest_framework.exceptions import ValidationError

from finance.enums import CategoryType
from finance.models import CategoryModel
from finance.repositories.category import CategoryRepository


class CategoryService:
    """
    Business logic layer.
    """

    @staticmethod
    @transaction.atomic
    def create_category(*, user, **kwargs) -> CategoryModel:
        name = kwargs.get("name")
        category_type = kwargs.get("type")

        if not name:
            raise ValidationError({"name": "نام دسته بندی الزامی است."})

        if not category_type:
            raise ValidationError({"type": "نوع دسته بندی الزامی است."})

        exists = CategoryRepository.exists(
            user_id=str(user.id),
            name=name,
            category_type=category_type,
        )

        if exists:
            raise ValidationError(
                {"name": ("دسته بندی با این نام و نوع در حال حاضر وجود دارد.")}
            )

        return CategoryRepository.create(
            user=user,
            **kwargs,
        )

    @staticmethod
    @transaction.atomic
    def update_category(
        *,
        user,
        category_id,
        **data,
    ) -> CategoryModel:

        category = CategoryRepository.get_user_category(
            user_id=user.id,
            category_id=category_id,
        )

        name = data.get(
            "name",
            category.name,
        )

        category_type = data.get(
            "type",
            category.type,
        )

        duplicate = CategoryRepository.exists(
            user_id=user.id,
            name=name,
            category_type=category_type,
            exclude_id=category.id,
        )

        if duplicate:
            raise ValidationError(
                {"name": ("دسته بندی با این نام و نوع در حال حاضر وجود دارد.")}
            )

        return CategoryRepository.update(
            category,
            **data,
        )
