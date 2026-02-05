from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


def get_from_email():
    """Get properly formatted from email address."""
    # Gmail requires from_email to match or include EMAIL_HOST_USER
    if settings.DEFAULT_FROM_EMAIL and '@' in settings.DEFAULT_FROM_EMAIL:
        return settings.DEFAULT_FROM_EMAIL
    elif settings.DEFAULT_FROM_EMAIL:
        # Format as "Display Name <email@example.com>"
        return f"{settings.DEFAULT_FROM_EMAIL} <{settings.EMAIL_HOST_USER}>"
    return settings.EMAIL_HOST_USER


def send_invoice_email(invoice, checkout_url):
    """Send invoice email with Stripe payment link."""
    if not invoice.customer or not invoice.customer.email:
        return False
    
    subject = f'Invoice {invoice.invoice_number} from Michaello Jewelry'
    
    context = {
        'invoice': invoice,
        'checkout_url': checkout_url,
    }
    
    html_message = render_to_string('notifications/email/invoice_email.html', context)
    plain_message = f"""
Dear {invoice.customer.name},

Please find your invoice {invoice.invoice_number} for €{invoice.total}.

Pay online: {checkout_url}

Thank you for your business!

Michaello Jewelry
"""
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=get_from_email(),
            recipient_list=[invoice.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_payment_confirmation_email(invoice):
    """Send payment confirmation email."""
    if not invoice.customer or not invoice.customer.email:
        return False
    
    subject = f'Payment Received - Invoice {invoice.invoice_number} from Michaello Jewelry'
    
    context = {
        'invoice': invoice,
    }
    
    html_message = render_to_string('notifications/email/payment_confirmation.html', context)
    plain_message = f"""
Dear {invoice.customer.name},

Thank you for your payment of €{invoice.total} for invoice {invoice.invoice_number}.

Your payment has been received and processed successfully.

Thank you for your business!

Michaello Jewelry
"""
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=get_from_email(),
            recipient_list=[invoice.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_certificate_email(certificate, customer):
    """Send certificate email with PDF attachment."""
    if not customer or not customer.email:
        return False
    
    subject = f'Jewelry Certificate - {certificate.certificate_number} from Michaello Jewelry'
    
    context = {
        'certificate': certificate,
        'customer': customer,
    }
    
    html_message = render_to_string('notifications/email/certificate_email.html', context)
    plain_message = f"""
Dear {customer.name},

Please find attached your jewelry certificate {certificate.certificate_number} from Michaello Jewelry.

Thank you for your purchase!

Michaello Jewelry
"""
    
    try:
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=get_from_email(),
            to=[customer.email],
        )
        email.content_subtype = 'html'
        email.body = html_message
        
        if certificate.pdf_file:
            email.attach_file(certificate.pdf_file.path)
        
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
