from rest_framework import serializers

from .category import CategorySerializer
from finance.enums import TransactionType
from finance.models import TransactionModel, CategoryModel


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction serializer for list
    """

    category = CategorySerializer()

    persian_date = serializers.SerializerMethodField()
    persian_month_name = serializers.SerializerMethodField()

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
            "persian_date",
            "persian_month_name",
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
            "persian_date",
            "persian_month_name",
        )

    def get_persian_date(self, obj):
        """Get Persian date"""
        return obj.get_persian_date()

    def get_persian_month_name(self, obj):
        """Get Persian month name"""
        return obj.get_persian_month_name()


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


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for create and update transaction
    """

    category_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Category ID (optional)",
        error_messages={
            "invalid": "شناسه دسته بندی معتبر نیست.",
        },
    )

    amount = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="Amount in Tomans (positive value)",
        error_messages={
            "required": "مبلغ الزامی است.",
            "min_value": "مبلغ باید بیشتر از صفر باشد.",
            "invalid": "مبلغ معتبر نیست.",
        },
    )

    # type = serializers.ChoiceField(
    #     choices=TransactionType.choices,
    #     required=True,
    #     error_messages={
    #         "required": "نوع تراکنش الزامی است.",
    #         "invalid_choice": "نوع تراکنش معتبر نیست.",
    #     },
    # )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=500,
        help_text="Transaction description",
        error_messages={
            "max_length": "توضیحات بیشتر از ۵۰۰ کاراکتر است.",
        },
    )

    date = serializers.DateField(
        required=False,
        help_text="Transaction date (Gregorian). If not provided, uses today.",
        error_messages={
            "invalid": "تاریخ معتبر نیست.",
        },
    )

    class Meta:
        model = TransactionModel
        fields = (
            "category_id",
            "amount",
            # "type",
            "description",
            "date",
        )

    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("مبلغ باید بیشتر از صفر باشد.")
        return value
