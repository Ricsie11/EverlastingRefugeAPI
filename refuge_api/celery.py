import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'refuge_api.settings')

app = Celery('refuge_api')

# Load settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Hardening beat schedule
app.conf.beat_schedule = {
    # Generate QR every Sunday 4:00 AM
    "generate-weekly-qr": {
        "task": "attendance.tasks.generate_weekly_qr_codes",
        "schedule": crontab(hour=4, minute=0, day_of_week=0),
        "options": {"queue": "high_priority"},
    },

    # Send attendance summary Sunday 1:10 PM
    "send-attendance-summary": {
        "task": "attendance.tasks.send_attendance_summary",
        "schedule": crontab(hour=13, minute=10, day_of_week=0),
        "options": {"queue": "low_priority"},
    },
}

# Timezone enforcement
app.conf.enable_utc = False
app.conf.timezone = 'Africa/Lagos'