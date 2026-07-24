from django.shortcuts import get_object_or_404


from finance.enums import CategoryType
from finance.models import CategoryModel


class CategoryRepository:
    """Only database operations."""

    @staticmethod
    def create(**kwargs):
        return CategoryModel.objects.create(**kwargs)

    @staticmethod
    def update(category: CategoryModel, **kwargs):
        for key, value in kwargs.items():
            setattr(
                category,
                key,
                value,
            )

        category.save(update_fields=list(kwargs.keys()))

        return category

    @staticmethod
    def get_user_category(user_id, category_id):

        return get_object_or_404(
            CategoryModel,
            id=category_id,
            user_id=user_id,
        )

    @staticmethod
    def get_user_categories(user_id: str):
        return CategoryModel.objects.filter(user_id=user_id).order_by("-created_at")

    @staticmethod
    def get_active_categories(user_id: str):
        return CategoryModel.objects.filter(
            user_id=user_id, is_archived=False
        ).order_by("-created_at")

    @staticmethod
    def exists(user_id, name, category_type, exclude_id=None):

        queryset = CategoryModel.objects.filter(
            user_id=user_id,
            name=name,
            type=category_type,
        )

        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        return queryset.exists()
