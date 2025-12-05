from django.contrib import admin
from .models import PayoutRequest


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'currency', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['id', 'recipient_details', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('amount', 'currency', 'recipient_details', 'status')
        }),
        ('Дополнительная информация', {
            'fields': ('comment', 'created_at', 'updated_at')
        }),
    )

