from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('add/', views.item_create, name='item_create'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('<int:pk>/json/', views.item_json, name='item_json'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
