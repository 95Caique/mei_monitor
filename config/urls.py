from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("telegram/", include("telegram_bot.urls", namespace='telegram_bot')),
    path("admin-panel/", include("adminpanel.urls", namespace='adminpanel')),
    path("", include("dashboard.urls")),



]
