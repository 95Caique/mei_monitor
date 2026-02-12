from django.urls import path
from .views import home, create_invoice, reports, reports_export

urlpatterns = [
    path("", home, name="dashboard"),
    path("invoice/create/", create_invoice, name="create_invoice"),
    path("reports/", reports, name="reports"),
    path("reports/export/", reports_export, name="reports_export"),
]
