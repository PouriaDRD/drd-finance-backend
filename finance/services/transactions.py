from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from finance.enums import TransactionType
from finance.repositories import TransactionRepository
from finance.models import TransactionModel, CategoryModel


class TransactionService:
    """
    Business logic layer for transactions.
    """

    @staticmethod
    @transaction.atomic
    def create_transaction(*, user, **kwargs) -> TransactionModel:
        """
        Create a new transaction.

        Args:
            user: User instance
            **kwargs: Transaction data (amount, type, category, description, date)

        Returns:
            TransactionModel: Created transaction

        Raises:
            ValidationError: If data is invalid
        """

        category_id = kwargs.get("category_id")
        if not category_id:
            raise ValidationError({"category_id": "شناسه دسته بندی الزامی است."})

        category = None

        try:
            category = CategoryModel.objects.get(
                id=category_id,
                user=user,
            )
        except CategoryModel.DoesNotExist:
            raise ValidationError(
                {"category_id": "دسته بندی پیدا نشد یا به شما تعلق ندارد."}
            )

        transaction_data = {
            "user": user,
            "amount": kwargs.get("amount", 0),
            "type": kwargs.get("type", TransactionType.INCOME),
            "description": kwargs.get("description", ""),
            "date": kwargs.get("date", timezone.now()),
            "category": category,
        }

        try:
            transaction_obj = TransactionRepository.create(**transaction_data)

            return transaction_obj

        except Exception as e:
            print(e)
            raise ValidationError({"error": "خطا در ایجاد تراکنش رخ داد."})

    @staticmethod
    @transaction.atomic
    def update_transaction(*, user, transaction_id, **data) -> TransactionModel:
        """
        Update an existing transaction.
        """

        try:
            transaction_obj = TransactionRepository.get_user_transaction(
                user_id=user.id,
                transaction_id=transaction_id,
            )
        except ObjectDoesNotExist:
            raise ValidationError(
                {"transaction_id": "تراکنش پیدا نشد یا به شما تعلق ندارد."}
            )

        if "category_id" in data:
            category_id = data["category_id"]
            if category_id:
                try:
                    category = CategoryModel.objects.get(
                        id=category_id,
                        user=user,
                    )
                    data["category"] = category
                except CategoryModel.DoesNotExist:
                    raise ValidationError(
                        {"category_id": "دسته بندی پیدا نشد یا به شما تعلق ندارد."}
                    )
            else:
                data["category"] = None

            # حذف category_id از data (چون در مدل نیست)
            data.pop("category_id", None)

        try:
            updated_transaction = TransactionRepository.update(transaction_obj, **data)

            return updated_transaction

        except Exception as e:
            raise ValidationError({"error": "خطا در به‌روزرسانی تراکنش رخ داد."})

    @staticmethod
    @transaction.atomic
    def delete_transaction(*, user, transaction_id) -> bool:
        """
        Delete a transaction.

        Args:
            user: User instance
            transaction_id: Transaction ID

        Returns:
            bool: True if deleted successfully

        Raises:
            ValidationError: If transaction not found
        """

        try:
            transaction_obj = TransactionRepository.get_user_transaction(
                user_id=user.id,
                transaction_id=transaction_id,
            )
        except ObjectDoesNotExist:
            raise ValidationError(
                {"transaction_id": "تراکنش پیدا نشد یا به شما تعلق ندارد."}
            )

        try:
            transaction_obj.delete()

            return True

        except Exception as e:
            raise ValidationError({"error": "خطا در حذف تراکنش رخ داد."})
