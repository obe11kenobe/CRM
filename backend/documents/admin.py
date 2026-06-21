from django.contrib import admin

from .models import MiningObject, License, DocumentDirection, Authority, DocumentTask


@admin.register(MiningObject)
class MiningObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('mining_object', 'number', 'status', 'issued_at', 'expires_at')
    list_filter = ('mining_object', 'status')
    search_fields = ('mining_object__name', 'number', 'status')


@admin.register(DocumentDirection)
class DocumentDirectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone', 'address')


@admin.register(DocumentTask)
class DocumentTaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'mining_object',
        'license_object',
        'direction',
        'authority',
        'status',
        'deadline',
        'responsible',
    )
    list_filter = (
        'mining_object',
        'direction',
        'authority',
        'status',
        'is_available',
        'deadline',
    )
    search_fields = (
        'title',
        'comment',
        'mining_object__name',
        'license_object__number',
        'authority__name',
    )
    readonly_fields = ('created_at', 'updated_at')
