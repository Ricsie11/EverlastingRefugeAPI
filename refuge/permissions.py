from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndActive(BasePermission):
    """
    Base safety check used internally by other permissions
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and
            user.is_authenticated and
            user.is_active
        )


class IsSuperUser(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user and
            user.is_authenticated and
            user.is_active and
            user.is_superuser and
            user.role == "SUPERUSER"
        )


class IsAdminOrSuperUser(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated or not user.is_active:
            return False

        if user.is_superuser and user.role == "SUPERUSER":
            return True

        if (
            user.role == "ADMIN" and
            user.is_staff
        ):
            return True

        return False


class IsSameGroup(BasePermission):
    """
    OBJECT-LEVEL PROTECTION:
    - Prevents cross-group access
    - Superuser bypasses
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated or not user.is_active:
            return False

        if user.is_superuser:
            return True

        return getattr(obj, "group", None) == user.group