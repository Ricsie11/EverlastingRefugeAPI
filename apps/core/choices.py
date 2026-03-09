from django.db import models

class AppRole(models.TextChoices):
    USER = "user", "User"
    ADMIN = "admin", "Admin"
    SUPERUSER = "superuser", "Superuser"


class GroupRole(models.TextChoices):
    MEMBER = "member", "Member"
    LEADER = "leader", "Leader"
