import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

from .models import Invoice, InvoiceLine
from .forms import InvoiceForm, InvoiceLineFormSet
from notifications.email_service import send_invoice_email, send_payment_confirmation_email

stripe.api_key = settings.STRIPE_SECRET_KEY

ITEMS_PER_PAGE = 10


@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('customer').all()
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    paginator = Paginator(invoices, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'sales/invoice_list.html', {'invoices': page_obj, 'page_obj': page_obj, 'status_filter': status_filter})


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice.objects.prefetch_related('lines', 'lines__item'), pk=pk)
    return render(request, 'sales/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            invoice.calculate_totals()
            invoice.save()
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect('sales:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = InvoiceLineFormSet()
    return render(request, 'sales/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice',
    })


@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status == 'paid':
        messages.error(request, 'Cannot edit a paid invoice.')
        return redirect('sales:invoice_detail', pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceLineFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            invoice.calculate_totals()
            invoice.save()
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully.')
            return redirect('sales:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceLineFormSet(instance=invoice)
    return render(request, 'sales/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': f'Edit {invoice.invoice_number}',
        'invoice': invoice,
    })


@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status == 'paid':
        messages.error(request, 'Cannot delete a paid invoice.')
        return redirect('sales:invoice_detail', pk=pk)
    
    if request.method == 'POST':
        number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice {number} deleted successfully.')
        return redirect('sales:invoice_list')
    return render(request, 'sales/invoice_confirm_delete.html', {'invoice': invoice})


@login_required
def invoice_send(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status != 'draft':
        messages.warning(request, 'Invoice has already been sent or processed.')
        return redirect('sales:invoice_detail', pk=pk)
    
    if not invoice.customer or not invoice.customer.email:
        messages.error(request, 'Cannot send invoice: customer has no email address.')
        return redirect('sales:invoice_detail', pk=pk)
    
    # Generate Stripe checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': invoice.currency,
                    'unit_amount': int(invoice.total * 100),
                    'product_data': {
                        'name': f'Invoice {invoice.invoice_number}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.STRIPE_SUCCESS_URL + f'?invoice_id={invoice.pk}',
            cancel_url=settings.STRIPE_CANCEL_URL + f'?invoice_id={invoice.pk}',
            metadata={'invoice_id': str(invoice.pk)},
        )
        invoice.stripe_checkout_session_id = checkout_session.id
        invoice.status = 'sent'
        invoice.save()
        
        # Send email with payment link
        email_sent = send_invoice_email(invoice, checkout_session.url)
        
        if email_sent:
            messages.success(request, f'Invoice {invoice.invoice_number} sent to {invoice.customer.email}.')
        else:
            messages.warning(request, f'Invoice {invoice.invoice_number} created but email failed to send. Payment link: {checkout_session.url}')
    except stripe.error.StripeError as e:
        messages.error(request, f'Stripe error: {str(e)}')
    
    return redirect('sales:invoice_detail', pk=pk)


@login_required
def invoice_void(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status == 'paid':
        messages.error(request, 'Cannot void a paid invoice.')
        return redirect('sales:invoice_detail', pk=pk)
    
    invoice.status = 'void'
    invoice.save()
    messages.success(request, f'Invoice {invoice.invoice_number} has been voided.')
    return redirect('sales:invoice_detail', pk=pk)


@login_required
def generate_payment_link(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status == 'paid':
        messages.error(request, 'Invoice has already been paid.')
        return redirect('sales:invoice_detail', pk=pk)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': invoice.currency,
                    'unit_amount': int(invoice.total * 100),
                    'product_data': {
                        'name': f'Invoice {invoice.invoice_number}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.STRIPE_SUCCESS_URL + f'?invoice_id={invoice.pk}',
            cancel_url=settings.STRIPE_CANCEL_URL + f'?invoice_id={invoice.pk}',
            metadata={'invoice_id': str(invoice.pk)},
        )
        invoice.stripe_checkout_session_id = checkout_session.id
        if invoice.status == 'draft':
            invoice.status = 'sent'
        invoice.save()
        
        return JsonResponse({'url': checkout_session.url})
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    print(f"[WEBHOOK] Received webhook request")
    print(f"[WEBHOOK] Signature present: {bool(sig_header)}")
    print(f"[WEBHOOK] Secret (first 10 chars): {webhook_secret[:10] if webhook_secret else 'EMPTY'}")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        print(f"[WEBHOOK] Event verified: {event['type']}")
    except ValueError as e:
        print(f"[WEBHOOK] ValueError: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"[WEBHOOK] SignatureVerificationError: {e}")
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        invoice_id = session.get('metadata', {}).get('invoice_id')
        print(f"[WEBHOOK] checkout.session.completed - invoice_id: {invoice_id}")
        
        if invoice_id:
            try:
                invoice = Invoice.objects.get(pk=invoice_id)
                print(f"[WEBHOOK] Found invoice: {invoice.invoice_number}, current status: {invoice.status}")
                if invoice.status != 'paid':
                    invoice.status = 'paid'
                    invoice.stripe_payment_intent_id = session.get('payment_intent')
                    invoice.save()
                    print(f"[WEBHOOK] Invoice marked as paid")
                    invoice.update_inventory_on_paid()
                    send_payment_confirmation_email(invoice)
                    print(f"[WEBHOOK] Inventory updated and email sent")
                else:
                    print(f"[WEBHOOK] Invoice already paid, skipping")
            except Invoice.DoesNotExist:
                print(f"[WEBHOOK] Invoice {invoice_id} not found!")
    
    return HttpResponse(status=200)


def payment_success(request):
    invoice_id = request.GET.get('invoice_id')
    invoice = None
    if invoice_id:
        invoice = Invoice.objects.filter(pk=invoice_id).first()
    return render(request, 'sales/payment_success.html', {'invoice': invoice})


def payment_cancel(request):
    invoice_id = request.GET.get('invoice_id')
    invoice = None
    if invoice_id:
        invoice = Invoice.objects.filter(pk=invoice_id).first()
    return render(request, 'sales/payment_cancel.html', {'invoice': invoice})


@login_required
def invoice_search(request):
    """Search invoices for autocomplete in certificate form."""
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    invoices = Invoice.objects.select_related('customer').filter(status='paid')
    
    if query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=query) | Q(customer__name__icontains=query)
        )
    
    # Limit results for performance
    invoices = invoices[:20]
    
    results = [
        {
            'id': inv.pk,
            'invoice_number': inv.invoice_number,
            'customer': inv.customer.name if inv.customer else 'Walk-in',
            'total': str(inv.total),
            'status': inv.get_status_display(),
            'text': f"{inv.invoice_number} - {inv.customer.name if inv.customer else 'Walk-in'} (€{inv.total})",
        }
        for inv in invoices
    ]
    
    return JsonResponse({'results': results})
