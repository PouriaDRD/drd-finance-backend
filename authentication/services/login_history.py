from user_agents import parse
from django.db import transaction
from rest_framework.request import Request

from accounts.models import UserModel
from accounts.repositories import UserRepository
from authentication.repositories import LoginHistoryRepository


class LoginHistoryService:
    """
    Login history service.
    """

    @staticmethod
    @transaction.atomic
    def create_success(user: UserModel, request: Request):

        login_info = LoginHistoryService.get_login_info(request)

        return LoginHistoryRepository.create(
            user=user,
            ip_address=login_info["ip_address"],
            user_agent=login_info["user_agent"],
            device=login_info["device"],
            browser=login_info["browser"],
            operating_system=login_info["os"],
            is_successful=True,
        )

    @staticmethod
    @transaction.atomic
    def create_failed(email: str, request: Request, reason: str):
        user = UserRepository.get_by_email(email)
        if not user:
            return

        login_info = LoginHistoryService.get_login_info(request)

        return LoginHistoryRepository.create(
            user=user,
            ip_address=login_info["ip_address"],
            user_agent=login_info["user_agent"],
            device=login_info["device"],
            browser=login_info["browser"],
            operating_system=login_info["os"],
            is_successful=False,
            failure_reason=reason,
        )

    @staticmethod
    def get_login_info(request: Request):
        user_agent_string = request.META.get("HTTP_USER_AGENT", "")
        ua = parse(user_agent_string)

        os = ua.os.family

        browser = f"{ua.browser.family} {ua.browser.version_string}"
        device = "Mobile" if ua.is_mobile else "PC" if ua.is_pc else "Tablet"

        ip_address = LoginHistoryService.get_client_ip(request)

        return {
            "browser": browser,
            "device": device,
            "ip_address": ip_address,
            "user_agent": ua,
            "os": os,
        }

    @staticmethod
    def get_client_ip(request: Request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
