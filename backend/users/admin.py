from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, JobTitle


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("username", "email", "photo", "date_birth")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительная информация", {"fields": ("photo", "date_birth")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ("job_title", "parent", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("job_title", "description")
    filter_horizontal = ("permissions",)