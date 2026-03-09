import uuid
from django.conf import settings
from django.db import models

class AttendanceCode(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(max_length=255)

    sunday_date = models.DateField()

    expires_at = models.DateTimeField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


class AttendanceRecord(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    code = models.ForeignKey(
        AttendanceCode,
        on_delete=models.CASCADE
    )

    scanned_at = models.DateTimeField(auto_now_add=True)
