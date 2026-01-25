from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.certificate_list, name='certificate_list'),
    path('create/', views.certificate_create, name='certificate_create'),
    path('<int:pk>/', views.certificate_detail, name='certificate_detail'),
    path('<int:pk>/download/', views.certificate_download, name='certificate_download'),
    path('<int:pk>/email/', views.certificate_email, name='certificate_email'),
    path('<int:pk>/delete/', views.certificate_delete, name='certificate_delete'),
]
