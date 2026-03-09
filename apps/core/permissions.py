from rest_framework.permissions import BasePermission
from apps.accounts.utils import has_role
from apps.core.choices import AppRole


class IsAdminOrSuperUser(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        return (
            has_role(user, AppRole.ADMIN)
            or has_role(user, AppRole.SUPERUSER)
        )


class IsSuperUser(BasePermission):

    def has_permission(self, request, view):
        return has_role(request.user, AppRole.SUPERUSER)
