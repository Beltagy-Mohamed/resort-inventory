from django.db.models import F

from .models import Product, SystemSettings
from inventory.decorators import is_the_leader


def inventory_notifications(request):
    """
    Makes low-stock / out-of-stock alerts and system settings
    available to every template (topbar bell, footer, etc.) without
    each view having to fetch them separately.

    Deliberately not a database-backed Notification model — the
    requirement is "show current low/out of stock", which is always
    derivable live from Product, so a stored notification table would
    just be another thing that can drift out of sync.
    """

    if not request.user.is_authenticated:
        return {}

    low_stock_qs = Product.objects.filter(
        quantity__lte=F("minimum_stock"),
        quantity__gt=0,
    ).order_by("quantity")

    out_of_stock_qs = Product.objects.filter(
        quantity=0
    ).order_by("-updated_at")

    alerts = list(out_of_stock_qs[:5]) + list(low_stock_qs[:5])

    return {
        "nav_low_stock_count": low_stock_qs.count(),
        "nav_out_of_stock_count": out_of_stock_qs.count(),
        "nav_alert_products": alerts[:6],
        "system_settings": SystemSettings.load(),
        "is_leader": is_the_leader(request.user),
    }
