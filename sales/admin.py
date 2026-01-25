from django.contrib import admin
from .models import Invoice, InvoiceLine


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invoice_number', 'customer__name']
    inlines = [InvoiceLineInline]
    readonly_fields = ['invoice_number', 'subtotal', 'total']
