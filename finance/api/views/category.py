import logging
from rest_framework import status
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import ListAPIView, CreateAPIView

from config.utils import APIResponse
from finance.services import CategoryService
from finance.repositories import CategoryRepository
from finance.api.serializers import CategorySerializer, CategoryCreateSerializer

logger = logging.getLogger("finance.category")


class MyCategoriesAPIView(ListAPIView):
    """
    API endpoint for user to get all of their categories.
    """

    http_method_names = ["get"]

    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):  # type: ignore
        qs = CategoryRepository.get_user_categories(str(self.request.user.id))  # type: ignore
        return qs

    def get(self, request: Request, *args, **kwargs):
        try:
            user = request.user
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            logger.info(f"User requested categories: {str(user)}")
            return APIResponse.success(
                data=serializer.data,
                message="داده های دسته بندی شما با موفقیت دریافت شد.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error getting user login history: {e}")
            return APIResponse.error(
                message="خطا در دریافت دسته بندی شما رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyActiveCategoriesAPIView(ListAPIView):
    """
    API endpoint for user to get all of their active categories.
    """

    http_method_names = ["get"]

    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):  # type: ignore
        qs = CategoryRepository.get_active_categories(str(self.request.user.id))  # type: ignore
        return qs

    def get(self, request: Request, *args, **kwargs):
        try:
            user = request.user
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            logger.info(f"User requested active categories: {str(user)}")
            return APIResponse.success(
                data=serializer.data,
                message="داده های دسته بندی فعال شما با موفقیت دریافت شد.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error getting user login history: {e}")
            return APIResponse.error(
                message="خطا در دریافت دسته بندی فعال شما رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CategoryCreateAPIView(CreateAPIView):
    """
    Create new category.
    """

    http_method_names = ["post"]

    permission_classes = [IsAuthenticated]
    serializer_class = CategoryCreateSerializer

    throttle_scope = "user"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request: Request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)

            category = CategoryService.create_category(
                user=request.user,
                **serializer.validated_data,
            )

            response_serializer = CategorySerializer(category)

            logger.info(
                f"Category created successfully: {category}, user: {request.user}"
            )
            return APIResponse.success(
                data=response_serializer.data,
                message="دسته بندی با موفقیت ایجاد شد.",
                status_code=status.HTTP_201_CREATED,
            )

        except ValidationError as e:
            logger.warning(f"Error creating category: {e.get_codes()}")
            if "name" in e.get_codes():  # type: ignore
                return APIResponse.error(
                    message="دسته بندی با این نام و نوع در حال حاضر وجود دارد.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            return APIResponse.error(
                message="خطا در ایجاد دسته بندی رخ داد.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception(f"Category creation failed: {e}")

            return APIResponse.error(
                message="خطا در ایجاد دسته بندی رخ داد.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
