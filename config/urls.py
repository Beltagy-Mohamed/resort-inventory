from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from inventory.api.main import api

from django.conf import settings
from django.conf.urls.static import static


from django.http import HttpResponse


import os
from django.core.exceptions import PermissionDenied

def require_setup_auth(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return True
    token = request.GET.get('token')
    expected = os.environ.get('SETUP_TOKEN')
    if expected and token == expected:
        return True
    raise PermissionDenied("Unauthorized access to setup/migrate endpoint.")


def remote_migrate(request):
    require_setup_auth(request)
    """Run migrations only — does NOT delete any data."""
    import django.core.management
    try:
        django.core.management.call_command('migrate', '--run-syncdb')
        return HttpResponse("Migrations applied successfully! (No data deleted)")
    except Exception as e:
        import traceback
        return HttpResponse("Error: " + traceback.format_exc(), status=500)

def remote_setup(request):
    require_setup_auth(request)
    """One-time production setup: run migrations + create admin if missing."""
    import django.core.management
    from django.contrib.auth.models import User
    try:
        django.core.management.call_command('migrate', '--run-syncdb')
        msg = "Migrations OK. "
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', '', 'admin')
            msg += "Admin created. "
        else:
            msg += "Admin already exists. "
        return HttpResponse(msg)
    except Exception as e:
        import traceback
        return HttpResponse("Error: " + traceback.format_exc(), status=500)

urlpatterns = [
    path("system-migrate/", remote_migrate),
    path("system-setup/", remote_setup),

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