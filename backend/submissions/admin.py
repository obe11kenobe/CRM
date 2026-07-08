from django.contrib import admin

from .models import AgencyResponse, DocumentRoute, SubmissionPackage


class AgencyResponseInline(admin.TabularInline):
    model = AgencyResponse
    extra = 0
    fields = ("response_type", "received_at", "correction_due_date", "created_by")
    readonly_fields = ("created_by",)


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
    ordering = ("route_id",)

@admin.register(SubmissionPackage)
class SubmissionPackageAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "route",
        "status",
        "outgoing_number",
        "agency_incoming_number",
        "sent_at",
        "registered_at",
        "created_by",
    )
    list_filter = (
        "status",
        "route",
        "sent_at",
        "registered_at",
    )
    search_fields = (
        "task__title",
        "route__route_id",
        "route__name",
        "outgoing_number",
        "agency_incoming_number",
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = [AgencyResponseInline]


@admin.register(AgencyResponse)
class AgencyResponseAdmin(admin.ModelAdmin):
    list_display = ("package", "response_type", "received_at", "correction_due_date", "created_by")
    list_filter = ("response_type",)
    search_fields = ("package__task__title", "comment")
    readonly_fields = ("created_at",)