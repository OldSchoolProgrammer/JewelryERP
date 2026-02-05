from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from crm.models import Supplier


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class JewelryItem(models.Model):
    METAL_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
        ('other', 'Other'),
    ]

    PURITY_CHOICES = [
        ('14K', '14K'),
        ('18K', '18K'),
        ('22K', '22K'),
        ('925K', '925K'),
        ('N/A', 'N/A'),
    ]

    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='jewelry_items')
    description = models.TextField(blank=True)
    metal = models.CharField(max_length=20, choices=METAL_CHOICES, default='gold')
    purity = models.CharField(max_length=20, choices=PURITY_CHOICES, default='N/A')
    weight_grams = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal('0'))])
    stone_details = models.TextField(blank=True, help_text='Gemstone type, carat, clarity, etc.')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    quantity_on_hand = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='jewelry_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sku} - {self.name}'

    @property
    def profit_margin(self):
        if self.cost_price and self.cost_price > 0:
            return ((self.sale_price - self.cost_price) / self.cost_price) * 100
        return Decimal('0')
