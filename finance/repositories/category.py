from finance.models import CategoryModel


class CategoryRepository:
    """Only database operations."""

    @staticmethod
    def create(**kwargs) -> CategoryModel:
        return CategoryModel.objects.create_user(**kwargs)  # type: ignore

    @staticmethod
    def get_user_categories(user_id: str):
        return CategoryModel.objects.filter(user_id=user_id).order_by("-created_at")

    @staticmethod
    def get_active_categories(user_id: str):
        return CategoryModel.objects.filter(
            user_id=user_id, is_archived=False
        ).order_by("-created_at")
