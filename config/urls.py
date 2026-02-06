"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('customers/', include(('crm.urls', 'crm'), namespace='crm')),
    path('suppliers/', include(('crm.urls_suppliers', 'crm'), namespace='crm_suppliers')),
    path('certificates/', include('documents.urls')),
]

if settings.DEBUG or getattr(settings, 'SERVE_MEDIA', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

