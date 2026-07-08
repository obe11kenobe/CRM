from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import AuditLogEntry, CustomUser, JobTitle


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "username",
        "email",
        "phone",
        "middle_name",
        "manager",
        "job_title",
        "photo",
        "date_birth",
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {
                "fields": (
                    "photo",
                    "date_birth",
                    "phone",
                    "middle_name",
                    "manager",
                    "job_title",
                    "email_verified",
                )
            },
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ("job_title", "parent", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("job_title", "description")
    filter_horizontal = ("permissions",)


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "model_name", "object_repr")
    list_filter = ("action", "model_name")
    search_fields = ("object_repr", "details", "user__username")
    readonly_fields = ("user", "action", "model_name", "object_id", "object_repr", "details", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
