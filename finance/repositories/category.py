from finance.enums import CategoryType
from finance.models import CategoryModel


class CategoryRepository:
    """Only database operations."""

    @staticmethod
    def create(**kwargs) -> CategoryModel:
        return CategoryModel.objects.create(**kwargs)

    @staticmethod
    def get_user_categories(user_id: str):
        return CategoryModel.objects.filter(user_id=user_id).order_by("-created_at")

    @staticmethod
    def get_active_categories(user_id: str):
        return CategoryModel.objects.filter(
            user_id=user_id, is_archived=False
        ).order_by("-created_at")

    @staticmethod
    def exists(user_id: str, name: str, category_type: CategoryType) -> bool:
        return CategoryModel.objects.filter(
            user_id=user_id,
            name=name,
            type=category_type,
        ).exists()
