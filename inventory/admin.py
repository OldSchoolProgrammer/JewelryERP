from django.contrib import admin
from .models import Category, JewelryItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(JewelryItem)
class JewelryItemAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'metal', 'sale_price', 'quantity_on_hand', 'is_active']
    list_filter = ['category', 'metal', 'is_active']
    search_fields = ['sku', 'name', 'description']
    list_editable = ['quantity_on_hand', 'is_active']
