"""
Leadership section API — protected by leadership_required decorator.
Accessible only to users with leader/superuser privileges (BRIEF §5.6).
"""
from ninja import Router
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from inventory.models import Product, InventoryTransaction, Stock
from inventory.decorators import is_the_leader
from .schemas import LeaderProductOut, LeaderStatsOut, TrackingType
from .auth import jwt_auth
from .products import _product_tracking_type
from ninja.errors import HttpError

router = Router(tags=["Leadership"])


def require_leader(request):
    if not is_the_leader(request.user):
        raise HttpError(404, "Not found")  # 404 not 403 — security by obscurity (BRIEF §decorators.py)


@router.get("/products/", response=list[LeaderProductOut], auth=jwt_auth)
def leader_products(request):
    """Leadership-restricted products — visible only to leader/superuser."""
    require_leader(request)
    qs = Product.all_objects.filter(
        is_leadership_restricted=True, is_archived=False
    ).select_related("category", "color", "size")
    return [
        LeaderProductOut(
            id=p.id, name=p.name,
            product_code=getattr(p, "product_code", str(p.id)),
            category=p.category.name if p.category else None,
            color=p.color.name if p.color else None,
            size=p.size.name if p.size else None,
            cost_price=p.cost_price,
            selling_price=p.selling_price,
            quantity=p.quantity,
            tracking_type=_product_tracking_type(p),
        )
        for p in qs
    ]


@router.get("/stats/", response=LeaderStatsOut, auth=jwt_auth)
def leader_stats(request):
    """Dashboard stats for the leadership section."""
    require_leader(request)
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    total_products = Product.all_objects.filter(is_archived=False).count()
    total_value    = (
        Product.all_objects.filter(is_archived=False)
        .aggregate(v=Sum("quantity"))["v"] or 0
    )
    low_stock = Product.all_objects.filter(
        is_archived=False,
        quantity__lte=5,
        quantity__gt=0,
    ).count()
    today_txns = InventoryTransaction.all_objects.filter(
        created_at__gte=today_start
    ).count()

    return LeaderStatsOut(
        total_products=total_products,
        total_value=total_value,
        low_stock_count=low_stock,
        today_transactions=today_txns,
    )
