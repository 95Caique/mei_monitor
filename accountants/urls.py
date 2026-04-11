from django.urls import path
from . import views

app_name = 'accountants'

urlpatterns = [
    path('', views.accountant_dashboard, name='dashboard'),
    
    # Perfil do contador
    path('profile/', views.accountant_profile_view, name='profile'),
    
    # Clientes
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/add/', views.client_create, name='client_create'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    path('clients/<int:client_id>/edit/', views.client_edit, name='client_edit'),
    path('clients/<int:client_id>/toggle/', views.client_toggle_status, name='client_toggle'),
    
    # Notas (invoices)
    path('clients/<int:client_id>/invoice/add/', views.invoice_create_for_client, name='invoice_create'),
    path('clients/<int:client_id>/invoice/<int:invoice_id>/cancel/', views.invoice_cancel_for_client, name='invoice_cancel'),
]

