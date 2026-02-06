from django import forms
from .models import JewelryItem, Category
from crm.models import Supplier


class JewelryItemForm(forms.ModelForm):
    class Meta:
        model = JewelryItem
        fields = [
            'sku', 'name', 'category', 'supplier', 'description', 'metal', 'purity',
            'weight_grams', 'stone_details', 'cost_price', 'sale_price',
            'quantity_on_hand', 'image', 'is_active'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'metal': forms.Select(attrs={'class': 'form-select'}),
            'purity': forms.Select(attrs={'class': 'form-select'}),
            'weight_grams': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stone_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity_on_hand': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
