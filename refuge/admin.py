from django.contrib import admin
from .models import CustomUser, Group, HouseFellowship, AttendanceQR, Attendance

# =======================
# Inlines
# =======================

class GroupInline(admin.TabularInline):
    model = Group
    extra = 0
    fields = ('name', 'description', 'created_by')
    readonly_fields = ('created_by',)

class HouseFellowshipInline(admin.TabularInline):
    model = HouseFellowship
    extra = 0
    fields = ('fellowship_name', 'location', 'fellowship_leader_name', 'leader_contact')
    readonly_fields = ('fellowship_leader_name', 'leader_contact')

# =======================
# CustomUser Admin
# =======================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'is_staff', 'is_active', 'group')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('id',)
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        ('Personal Info', {'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number', 'group')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    inlines = [GroupInline, HouseFellowshipInline]

    # Role-based permissions
    def has_add_permission(self, request):
        return request.user.role in ['ADMIN', 'SUPERUSER']

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'SUPERUSER':
            return True
        if request.user.role == 'ADMIN':
            if obj and obj.role == 'USER':
                return True
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'SUPERUSER'


# =======================
# Group Admin
# =======================
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_by', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_by',)
    ordering = ('id',)
    readonly_fields = ('created_by', 'created_at')

    def has_add_permission(self, request):
        return request.user.role in ['ADMIN', 'SUPERUSER']

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'SUPERUSER':
            return True
        if request.user.role == 'ADMIN':
            if obj and obj.created_by and obj.created_by.role == 'USER':
                return True
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'SUPERUSER'


# =======================
# HouseFellowship Admin
# =======================
@admin.register(HouseFellowship)
class HouseFellowshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'fellowship_name', 'location', 'fellowship_leader_name', 'created_by', 'created_at')
    search_fields = ('fellowship_name', 'fellowship_leader_name')
    list_filter = ('created_by',)
    ordering = ('id',)
    readonly_fields = ('created_by', 'created_at')

    def has_add_permission(self, request):
        return request.user.role in ['ADMIN', 'SUPERUSER']

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'SUPERUSER':
            return True
        if request.user.role == 'ADMIN':
            if obj and obj.created_by and obj.created_by.role == 'USER':
                return True
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'SUPERUSER'


# =======================
# AttendanceQR Admin
# =======================
@admin.register(AttendanceQR)
class AttendanceQRAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'token', 'is_active', 'created_by', 'created_at', 'expires_at')
    search_fields = ('group__name', 'token')
    list_filter = ('is_active', 'group')
    ordering = ('id',)
    readonly_fields = ('qr_image', 'token', 'created_at', 'expires_at', 'created_by')

    def has_add_permission(self, request):
        return request.user.role in ['ADMIN', 'SUPERUSER']

    def has_change_permission(self, request, obj=None):
        return request.user.role in ['ADMIN', 'SUPERUSER']

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'SUPERUSER'


# =======================
# Attendance Admin
# =======================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group', 'qr_session', 'scanned_at')
    search_fields = ('user__email', 'group__name', 'qr_session__token')
    list_filter = ('group',)
    ordering = ('id',)
    readonly_fields = ('scanned_at',)

    def has_add_permission(self, request):
        return request.user.role in ['ADMIN', 'SUPERUSER']

    def has_change_permission(self, request, obj=None):
        return request.user.role in ['ADMIN', 'SUPERUSER']

    def has_delete_permission(self, request, obj=None):
        return request.user.role == 'SUPERUSER'