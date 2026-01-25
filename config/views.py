from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    from inventory.models import JewelryItem
    from crm.models import Customer, Supplier
    from sales.models import Invoice

    context = {
        'item_count': JewelryItem.objects.count(),
        'customer_count': Customer.objects.count(),
        'supplier_count': Supplier.objects.count(),
        'invoice_count': Invoice.objects.count(),
        'recent_invoices': Invoice.objects.select_related('customer').order_by('-created_at')[:5],
        'low_stock_items': JewelryItem.objects.filter(quantity_on_hand__lte=5, is_active=True)[:5],
    }
    return render(request, 'dashboard.html', context)
