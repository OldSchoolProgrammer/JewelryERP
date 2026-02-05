from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.core.paginator import Paginator

from .models import Certificate
from .forms import CertificateForm
from .pdf_generator import generate_certificate_pdf
from notifications.email_service import send_certificate_email

ITEMS_PER_PAGE = 10


@login_required
def certificate_list(request):
    certificates = Certificate.objects.select_related('item', 'invoice', 'customer').all()
    
    paginator = Paginator(certificates, ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'documents/certificate_list.html', {'certificates': page_obj, 'page_obj': page_obj})


@login_required
def certificate_detail(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related('item', 'invoice', 'customer'), pk=pk)
    return render(request, 'documents/certificate_detail.html', {'certificate': certificate})


@login_required
def certificate_create(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save()
            generate_certificate_pdf(certificate)
            messages.success(request, f'Certificate {certificate.certificate_number} created successfully.')
            return redirect('documents:certificate_detail', pk=certificate.pk)
    else:
        form = CertificateForm()
        # Pre-fill item if provided in query params
        item_id = request.GET.get('item')
        invoice_id = request.GET.get('invoice')
        customer_id = request.GET.get('customer')
        if item_id:
            form.fields['item'].initial = item_id
        if invoice_id:
            form.fields['invoice'].initial = invoice_id
        if customer_id:
            form.fields['customer'].initial = customer_id
    return render(request, 'documents/certificate_form.html', {'form': form, 'title': 'Generate Certificate'})


@login_required
def certificate_download(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    if not certificate.pdf_file:
        generate_certificate_pdf(certificate)
    
    if not certificate.pdf_file:
        raise Http404("Certificate PDF not found")
    
    return FileResponse(
        certificate.pdf_file.open('rb'),
        as_attachment=True,
        filename=f'{certificate.certificate_number}.pdf'
    )


@login_required
def certificate_email(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related('item', 'invoice', 'invoice__customer', 'customer'), pk=pk)
    
    customer = None
    # Check for direct customer link first, then fall back to invoice customer
    if certificate.customer:
        customer = certificate.customer
    elif certificate.invoice and certificate.invoice.customer:
        customer = certificate.invoice.customer
    
    if not customer or not customer.email:
        messages.error(request, 'No customer email found for this certificate.')
        return redirect('documents:certificate_detail', pk=pk)
    
    if not certificate.pdf_file:
        generate_certificate_pdf(certificate)
    
    if send_certificate_email(certificate, customer):
        messages.success(request, f'Certificate sent to {customer.email}.')
    else:
        messages.error(request, 'Failed to send certificate email.')
    
    return redirect('documents:certificate_detail', pk=pk)


@login_required
def certificate_delete(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        number = certificate.certificate_number
        if certificate.pdf_file:
            certificate.pdf_file.delete()
        certificate.delete()
        messages.success(request, f'Certificate {number} deleted successfully.')
        return redirect('documents:certificate_list')
    return render(request, 'documents/certificate_confirm_delete.html', {'certificate': certificate})
