from django.urls import path
from .views import home, create_invoice, reports, reports_export, reports_export_pdf, notifications_api
from .views import manage_invoices, edit_invoice, cancel_invoice, delete_invoice

urlpatterns = [
    path("", home, name="dashboard"),
    path("invoice/create/", create_invoice, name="create_invoice"),
    path("invoices/", manage_invoices, name="manage_invoices"),
    path("invoice/<int:invoice_id>/edit/", edit_invoice, name="edit_invoice"),
    path("invoice/<int:invoice_id>/cancel/", cancel_invoice, name="cancel_invoice"),
    path("invoice/<int:invoice_id>/delete/", delete_invoice, name="delete_invoice"),
    path("reports/", reports, name="reports"),
    path("reports/export/", reports_export, name="reports_export"),
    path("reports/export/pdf/", reports_export_pdf, name="reports_export_pdf"),
    path("api/notifications/", notifications_api, name="notifications_api"),
]
