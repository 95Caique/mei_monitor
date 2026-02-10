from django.urls import path
from .views import home, create_invoice

urlpatterns = [
    path("", home, name="dashboard"),
    path("invoice/create/", create_invoice, name="create_invoice"),
]
