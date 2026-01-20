from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
import uuid
from django.utils import timezone
from io import BytesIO
import qrcode
import secrets
from django.core.files import File


# Create your models here.
class CustomUser (AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=[('USER', 'User'), ('ADMIN', 'Admin'), ('SUPERUSER', 'Superuser')],
        default='USER'
    )
    phone_number = PhoneNumberField(blank=True)
    email = models.EmailField(unique=True, blank=False)
    group = models.ForeignKey(
        'Group',
        on_delete = models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]


    def __str__(self):
        return self.username
    

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'groups_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class HouseFellowship(models.Model):
    fellowship_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    fellowship_leader_name = models.CharField(max_length=200)
    leader_contact = PhoneNumberField(blank=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.SET_NULL,
        null = True,
        related_name = "house_fellowship_centers"
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.fellowship_name + "at" + self.location
    

class AttendanceQR(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    qr_image = models.ImageField(upload_to='qrcodes/')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="qr_created"
    )

    def save(self, *args, **kwargs):
        #Only generate QR once
        if not self.qr_image:

          # Generate a unique token for scanning
            self.token = secrets.token_urlsafe(16)

            # Generate QR with token as data
            qr = qrcode.make(self.token)
            buffer = BytesIO()
            qr.save(buffer)
            self.qr_image.save(f"{self.group.name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.png", File(buffer), save=False)

              # Set expiration to 1 PM on the day of creation if not already set
        if not self.expires_at:
            self.expires_at = self.created_at.replace(hour=13, minute=0, second=0, microsecond=0)

            super().save(*args, **kwargs)


    def is_valid(self):
        """Check if the QR is active and not expired"""
        return self.is_active and timezone.now() <= self.expires_at
    
    def __str__(self):
        return f"QR for {self.group.name}"


class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    qr_session = models.ForeignKey(AttendanceQR, on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ("user", "qr_session")  # ONE scan per QR

    def __str__(self):
        return f"{self.user.email} - {self.scanned_at}"