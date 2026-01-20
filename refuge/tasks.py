from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Group, AttendanceQR
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def generate_weekly_qr_codes(self):
    """
    - Runs every Sunday at 4 AM
    - One active QR per group
    - Deactivates old QR
    - Creates new QR
    - Emails admin/superuser (non-blocking)
    - Logs everything
    """

    now = timezone.now()
    created_count = 0

    logger.info(f"[QR TASK START] {now}")

    for group in Group.objects.all():
        try:
            with transaction.atomic():
                # 1. Deactivate old QR
                AttendanceQR.objects.filter(
                    group=group,
                    is_active=True
                ).update(is_active=False)

                # 2. Find admin / superuser
                admin_user = User.objects.filter(
                    group=group,
                    role__in=["ADMIN", "SUPERUSER"]
                ).first()

                # 3. Create new QR
                qr = AttendanceQR.objects.create(
                    group=group,
                    created_by=admin_user
                )

                created_count += 1

            # 4. Send email (OUTSIDE transaction, non-blocking)
            if admin_user and admin_user.email:
                try:
                    send_mail(
                        subject=f"New Attendance QR Generated - {group.name}",
                        message=(
                            f"A new attendance QR has been generated for {group.name}.\n\n"
                            f"Valid until 1:00 PM today.\n\n"
                            f"Please log in to view the QR."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin_user.email],
                        fail_silently=True
                    )
                except Exception as mail_error:
                    logger.warning(
                        f"[QR EMAIL FAILED] {admin_user.email} | {mail_error}"
                    )

        except Exception as e:
            logger.error(
                f"[QR TASK ERROR] Group={group.id} | {str(e)}",
                exc_info=True
            )
            raise

    logger.info(
        f"[QR TASK END] Generated {created_count} QR codes at {timezone.now()}"
    )

    return {
        "status": "success",
        "generated": created_count,
        "timestamp": str(timezone.now())
    }