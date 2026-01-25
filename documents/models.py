from django.db import models
from django.utils import timezone

from inventory.models import JewelryItem
from sales.models import Invoice


class Certificate(models.Model):
    item = models.ForeignKey(JewelryItem, on_delete=models.CASCADE, related_name='certificates')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    certificate_number = models.CharField(max_length=50, unique=True, editable=False)
    issued_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return self.certificate_number

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        super().save(*args, **kwargs)

    def generate_certificate_number(self):
        today = timezone.now()
        prefix = f"CERT-{today.strftime('%Y%m%d')}"
        last_cert = Certificate.objects.filter(certificate_number__startswith=prefix).order_by('-certificate_number').first()
        if last_cert:
            last_num = int(last_cert.certificate_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f"{prefix}-{new_num:04d}"
