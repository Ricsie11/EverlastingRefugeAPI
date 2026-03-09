from apps.core.choices import AppRole
from .models import UserRole


def has_role(user, role: AppRole):
    """
    Checks if a user has a specific application role.
    """
    if not user.is_authenticated:
        return False
    return UserRole.objects.filter(user=user, role=role).exists()
