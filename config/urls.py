from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from inventory.api.main import api

from django.conf import settings
from django.conf.urls.static import static


from django.http import HttpResponse

def remote_migrate(request):
    import django.core.management
    try:
        django.core.management.call_command('migrate')
        
        # Now clear the data as requested by the user
        from inventory.models import Product, InventoryTransaction, ActivityLog, Partner
        InventoryTransaction.objects.all().delete()
        ActivityLog.objects.all().delete()
        Product.objects.all().delete()
        Partner.objects.all().delete()
        
        return HttpResponse("Migration and Data Wipe successful!")
    except Exception as e:
        import traceback
        return HttpResponse("Error: " + traceback.format_exc(), status=500)

urlpatterns = [
    path("system-migrate/", remote_migrate),

    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("", include("inventory.urls")),
    path("chat/", include("chat.urls")),
    path("api/v1/", api.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )