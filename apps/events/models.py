import uuid
from django.conf import settings
from django.db import models

class Event(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    event_date = models.DateField()
    event_day = models.CharField(max_length=20)

    tag = models.CharField(max_length=50, default="Event")

    image = models.ImageField(upload_to="event-images/", blank=True, null=True)

    youtube_url = models.URLField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
