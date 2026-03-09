from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/groups/", include("apps.groups.urls")),
    path("api/events/", include("apps.events.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
]
