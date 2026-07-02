from django.contrib import admin

from .models import MiningObject, License, DocumentDirection, Authority, DocumentTask


class LicenseInline(admin.TabularInline):
    model = License
    extra = 1
    fields = ('number', 'status', 'issued_at', 'expires_at')


@admin.register(MiningObject)
class MiningObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'nvos_category', 'municipality', 'created_at', 'updated_at')
    list_filter = ('is_active', 'nvos_category', 'created_at')
    search_fields = ('name', 'description', 'cadastral_number', 'municipality')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LicenseInline]


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('mining_object', 'number', 'status', 'issued_at', 'expires_at', 'is_expired', 'is_expiring_soon_flag')
    list_filter = ('mining_object', 'status')
    search_fields = ('mining_object__name', 'number', 'status')

    @admin.display(boolean=True, description='Истекла')
    def is_expired(self, obj):
        return obj.is_expired

    @admin.display(boolean=True, description='Истекает в 90 дн.')
    def is_expiring_soon_flag(self, obj):
        return obj.is_expiring_soon()


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
