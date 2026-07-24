from rest_framework import serializers

from .category import CategorySerializer
from finance.enums import TransactionType
from finance.models import TransactionModel, CategoryModel


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction serializer for list
    """

    category = CategorySerializer()

    class Meta:
        model = TransactionModel

        fields = (
            "id",
            "category",
            "description",
            "amount",
            "type",
            "date",
            "month",
            "year",
            "updated_at",
            "created_at",
        )

        read_only_fields = (
            "id",
            "category",
            "description",
            "amount",
            "type",
            "date",
            "month",
            "year",
            "updated_at",
            "created_at",
        )


class PersianMonthSummarySerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    month_name = serializers.CharField()

    income = serializers.IntegerField()
    expense = serializers.IntegerField()
    balance = serializers.IntegerField()

    count = serializers.IntegerField()

    transactions = TransactionSerializer(many=True)


class YearlySummaryItemSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    month_name = serializers.CharField()

    income = serializers.IntegerField()
    expense = serializers.IntegerField()
    balance = serializers.IntegerField()

    count = serializers.IntegerField()


class YearlySummarySerializer(serializers.Serializer):
    year = serializers.IntegerField()

    monthly_report = YearlySummaryItemSerializer(
        many=True,
    )

    total_income = serializers.IntegerField()
    total_expense = serializers.IntegerField()
    total_balance = serializers.IntegerField()
