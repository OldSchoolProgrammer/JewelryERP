from django import forms
from .models import Certificate
from inventory.models import JewelryItem
from sales.models import Invoice
from crm.models import Customer


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['item', 'invoice', 'customer']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'invoice': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = JewelryItem.objects.filter(is_active=True)
        self.fields['invoice'].queryset = Invoice.objects.filter(status='paid')
        self.fields['invoice'].required = False
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['customer'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        invoice = cleaned_data.get('invoice')
        customer = cleaned_data.get('customer')
        
        # Ensure at least one of invoice or customer is provided, but not both
        if invoice and customer:
            raise forms.ValidationError('Please select either an invoice or a customer, not both.')
        
        return cleaned_data
