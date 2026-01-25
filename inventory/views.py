from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from .models import JewelryItem, Category
from .forms import JewelryItemForm, CategoryForm


@login_required
def item_list(request):
    items = JewelryItem.objects.select_related('category')
    
    search = request.GET.get('search', '')
    if search:
        items = items.filter(Q(sku__icontains=search) | Q(name__icontains=search))
    
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    metal = request.GET.get('metal')
    if metal:
        items = items.filter(metal=metal)
    
    categories = Category.objects.all()
    
    return render(request, 'inventory/item_list.html', {
        'items': items,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'selected_metal': metal,
    })


@login_required
def item_detail(request, pk):
    item = get_object_or_404(JewelryItem, pk=pk)
    return render(request, 'inventory/item_detail.html', {'item': item})


@login_required
def item_create(request):
    if request.method == 'POST':
        form = JewelryItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Item "{item.name}" created successfully.')
            return redirect('inventory:item_list')
    else:
        form = JewelryItemForm()
    return render(request, 'inventory/item_form.html', {'form': form, 'title': 'Add New Item'})


@login_required
def item_edit(request, pk):
    item = get_object_or_404(JewelryItem, pk=pk)
    if request.method == 'POST':
        form = JewelryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Item "{item.name}" updated successfully.')
            return redirect('inventory:item_list')
    else:
        form = JewelryItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form, 'title': f'Edit {item.sku}', 'item': item})


@login_required
def item_delete(request, pk):
    item = get_object_or_404(JewelryItem, pk=pk)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f'Item "{name}" deleted successfully.')
        return redirect('inventory:item_list')
    return render(request, 'inventory/item_confirm_delete.html', {'item': item})


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('inventory:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {'form': form, 'title': f'Edit {category.name}'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/category_confirm_delete.html', {'category': category})


@login_required
def item_json(request, pk):
    """Return item details as JSON for invoice form auto-population."""
    item = get_object_or_404(JewelryItem, pk=pk)
    return JsonResponse({
        'id': item.pk,
        'sku': item.sku,
        'name': item.name,
        'description': f"{item.name} - {item.sku}",
        'sale_price': str(item.sale_price),
        'quantity_on_hand': item.quantity_on_hand,
    })
