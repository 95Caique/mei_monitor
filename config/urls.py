from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("hijack/", include("hijack.urls")),
    path("accounts/", include("accounts.urls")),
    path("telegram/", include("telegram_bot.urls", namespace='telegram_bot')),
    path("admin-panel/", include("adminpanel.urls", namespace='adminpanel')),
    path("accountants/", include("accountants.urls", namespace='accountants')),
    path("", include("dashboard.urls")),
]

if settings.DEBUG:
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

