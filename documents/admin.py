from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'item', 'invoice', 'issued_at']
    list_filter = ['issued_at']
    search_fields = ['certificate_number', 'item__sku', 'item__name']
    readonly_fields = ['certificate_number']
