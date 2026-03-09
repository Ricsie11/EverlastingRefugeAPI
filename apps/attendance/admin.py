from django.contrib import admin
from .models import AttendanceCode, AttendanceRecord

@admin.register(AttendanceCode)
class AttendanceCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'sunday_date', 'expires_at')
    search_fields = ('code',)

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'scanned_at')
    search_fields = ('user__username', 'code__code')
