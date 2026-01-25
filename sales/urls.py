from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('search/', views.invoice_search, name='invoice_search'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('<int:pk>/send/', views.invoice_send, name='invoice_send'),
    path('<int:pk>/void/', views.invoice_void, name='invoice_void'),
    path('<int:pk>/generate-payment-link/', views.generate_payment_link, name='generate_payment_link'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
]
