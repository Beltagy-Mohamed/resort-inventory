"""
Delta sync endpoint — mobile pulls updates since last_synced_at.
The mobile only sends Deltas, never final quantities (BRIEF §0.2).
"""
from ninja import Router, Query
from django.utils import timezone
from datetime import datetime
import time
from inventory.models import Product, Stock
from inventory.decorators import is_the_leader
from .schemas import DeltaResponse, ProductDetail, WarehouseStockItem, TrackingType
from .auth import jwt_auth
from .products import _product_tracking_type

router = Router(tags=["Sync"])


@router.get("/delta/", response=DeltaResponse, auth=jwt_auth)
def get_delta(request, since: int = Query(0, description="Epoch milliseconds — last successful sync timestamp")):
    """
    Returns all products updated since the given timestamp.
    Mobile uses this to keep Room DB in sync without a full refresh.
    """
    since_dt = datetime.fromtimestamp(since / 1000, tz=timezone.utc) if since > 0 else None

    if is_the_leader(request.user):
        qs = Product.all_objects.select_related("category", "color", "size")
    else:
        qs = Product.objects.select_related("category", "color", "size")

    qs = qs.filter(is_archived=False)
    if since_dt:
        qs = qs.filter(updated_at__gte=since_dt)

    product_ids = [p.id for p in qs]
    stock_map: dict[int, list] = {}
    for s in Stock.all_objects.filter(product_id__in=product_ids).select_related("warehouse"):
        stock_map.setdefault(s.product_id, []).append(
            WarehouseStockItem(
                warehouse_id=s.warehouse_id,
                warehouse_name=s.warehouse.name,
                quantity=s.quantity,
            )
        )

    products_out = []
    for p in qs:
        products_out.append(ProductDetail(
            id           = p.id,
            name         = p.name,
            product_code = getattr(p, "product_code", str(p.id)),
            category     = p.category.name if p.category else None,
            color        = p.color.name    if p.color    else None,
            size         = p.size.name     if p.size     else None,
            cost_price   = p.cost_price,
            selling_price= p.selling_price,
            quantity     = p.quantity,
            minimum_stock= p.minimum_stock,
            tracking_type= _product_tracking_type(p),
            is_archived  = p.is_archived,
            is_leader_only= p.is_leadership_restricted,
            stock_by_warehouse=stock_map.get(p.id, []),
        ))

    return DeltaResponse(
        products=products_out,
        last_synced_at=int(time.time() * 1000),
    )
