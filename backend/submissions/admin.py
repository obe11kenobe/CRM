from django.contrib import admin

from .models import DocumentRoute


@admin.register(DocumentRoute)
class DocumentRouteAdmin(admin.ModelAdmin):
    list_display = (
        "route_id",
        "name",
        "authority",
        "submission_channel",
        "risk_level",
        "allow_auto_generation",
        "is_active",
    )
    list_filter = (
        "submission_channel",
        "risk_level",
        "allow_auto_generation",
        "is_active",
    )
    search_fields = (
        "route_id",
        "name",
        "document_process",
        "authority__name",
    )
    readonly_fields = ("created_at", "updated_at")