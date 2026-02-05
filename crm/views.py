from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Customer, Supplier
from .forms import CustomerForm, SupplierForm

ITEMS_PER_PAGE = 10


# Customer Views
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search))
    
    paginator = Paginator(customers, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'crm/customer_list.html', {'customers': page_obj, 'page_obj': page_obj, 'search': search})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'crm/customer_detail.html', {'customer': customer})


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" created successfully.')
            return redirect('crm:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'crm/customer_form.html', {'form': form, 'title': 'Add Customer'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Customer "{customer.name}" updated successfully.')
            return redirect('crm:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'crm/customer_form.html', {'form': form, 'title': f'Edit {customer.name}'})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f'Customer "{name}" deleted successfully.')
        return redirect('crm:customer_list')
    return render(request, 'crm/customer_confirm_delete.html', {'customer': customer})


@login_required
def customer_search(request):
    """JSON endpoint for searching customers (for Tom Select dropdowns)."""
    query = request.GET.get('q', '').strip()
    customers = Customer.objects.all()
    
    if query:
        customers = customers.filter(
            Q(name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone__icontains=query)
        )
    
    customers = customers[:20]  # Limit results
    
    results = [{
        'id': customer.id,
        'text': customer.name,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
    } for customer in customers]
    
    return JsonResponse({'results': results})


# Supplier Views
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    search = request.GET.get('search', '')
    if search:
        suppliers = suppliers.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search))
    
    paginator = Paginator(suppliers, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'crm/supplier_list.html', {'suppliers': page_obj, 'page_obj': page_obj, 'search': search})


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'crm/supplier_detail.html', {'supplier': supplier})


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" created successfully.')
            return redirect('crm_suppliers:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'crm/supplier_form.html', {'form': form, 'title': 'Add Supplier'})


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Supplier "{supplier.name}" updated successfully.')
            return redirect('crm_suppliers:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'crm/supplier_form.html', {'form': form, 'title': f'Edit {supplier.name}'})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        messages.success(request, f'Supplier "{name}" deleted successfully.')
        return redirect('crm_suppliers:supplier_list')
    return render(request, 'crm/supplier_confirm_delete.html', {'supplier': supplier})
