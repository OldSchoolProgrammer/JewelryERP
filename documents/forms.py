from django import forms
from .models import Certificate
from inventory.models import JewelryItem
from sales.models import Invoice


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['item', 'invoice']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'invoice': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = JewelryItem.objects.filter(is_active=True)
        self.fields['invoice'].queryset = Invoice.objects.filter(status='paid')
        self.fields['invoice'].required = False
