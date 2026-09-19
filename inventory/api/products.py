"""
Product endpoints.
search/ is the most critical endpoint in the system (BRIEF §5.2, §13).
NOTE: barcode is absent from all responses (BRIEF §0.1).
"""
from ninja import Router, Query
from typing import Optional
from datetime import date, timedelta
from django.db.models import Q, Sum
from inventory.models import Product, Stock, InventoryTransaction
from inventory.decorators import is_the_leader
from .schemas import (
    ProductSearchResponse, ProductSearchItem, ProductDetail,
    WarehouseStockItem, BatchOut, BatchListResponse,
    SerialOut, TrackingType,
)
from .auth import jwt_auth

router = Router(tags=["Products"])


def _product_tracking_type(product: Product) -> TrackingType:
    """
    tracking_type is an immutable property of the PRODUCT (BRIEF §3).
    Falls back to NONE if the field does not exist yet on the model.
    """
    raw = getattr(product, "tracking_type", "NONE") or "NONE"
    try:
        return TrackingType(raw)
    except ValueError:
        return TrackingType.NONE


@router.get("/search/", response=ProductSearchResponse, auth=jwt_auth)
def search_products(
    request,
    q:         str           = Query("", description="Full-text search on name or product_code"),
    category:  Optional[str] = Query(None),
    color:     Optional[str] = Query(None),
    size:      Optional[str] = Query(None),
    warehouse: Optional[int] = Query(None, description="Scope stock to this warehouse"),
    page:      int           = Query(1, ge=1),
    page_size: int           = Query(30, ge=1, le=100),
):
    """
    Primary search endpoint.
    Returns: name + product_code + color + size + warehouse_stock (single-line render rule BRIEF §11.11).
    barcode is intentionally absent from the response (BRIEF §0.1).
    """
    qs = Product.objects.select_related("category", "color", "size")

    # Leader products filtered by PublicManager already — normal users can never see them
    # Leaders (is_the_leader) get all products
    if is_the_leader(request.user):
        qs = Product.all_objects.select_related("category", "color", "size")

    qs = qs.filter(is_archived=False)

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(product_code__icontains=q) if hasattr(Product, "product_code") else Q(name__icontains=q))

    if category:
        qs = qs.filter(category__name__iexact=category)
    if color:
        qs = qs.filter(color__name__iexact=color)
    if size:
        qs = qs.filter(size__name__iexact=size)

    count  = qs.count()
    offset = (page - 1) * page_size
    items  = qs.order_by("name")[offset: offset + page_size]

    # Build stock lookup for requested warehouse
    if warehouse:
        stock_map = {
            s.product_id: s.quantity
            for s in Stock.all_objects.filter(
                product_id__in=[p.id for p in items],
                warehouse_id=warehouse,
            )
        }
    else:
        stock_map = {}

    results = []
    for p in items:
        wh_stock = stock_map.get(p.id, p.quantity)
        results.append(ProductSearchItem(
            id             = p.id,
            name           = p.name,
            product_code   = getattr(p, "product_code", str(p.id)),
            color          = p.color.name if p.color else None,
            size           = p.size.name  if p.size  else None,
            warehouse_stock= wh_stock,
            tracking_type  = _product_tracking_type(p),
        ))

    next_url = f"?page={page+1}" if offset + page_size < count else None
    return ProductSearchResponse(count=count, next=next_url, results=results)


@router.get("/{product_id}/", response=ProductDetail, auth=jwt_auth)
def get_product(request, product_id: int):
    """Product detail including stock per warehouse."""
    from ninja.errors import HttpError
    try:
        if is_the_leader(request.user):
            p = Product.all_objects.select_related("category", "color", "size").get(pk=product_id)
        else:
            p = Product.objects.select_related("category", "color", "size").get(pk=product_id)
    except Product.DoesNotExist:
        raise HttpError(404, "الصنف غير موجود")

    stocks = Stock.all_objects.filter(product=p).select_related("warehouse")
    stock_by_wh = [
        WarehouseStockItem(
            warehouse_id=s.warehouse_id,
            warehouse_name=s.warehouse.name,
            quantity=s.quantity,
        )
        for s in stocks
    ]
    return ProductDetail(
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
        stock_by_warehouse=stock_by_wh,
    )


@router.get("/{product_id}/batches/", response=BatchListResponse, auth=jwt_auth)
def get_batches_fefo(request, product_id: int, warehouse_id: int = Query(...)):
    """
    FEFO-ordered batches for BATCH_EXPIRY products.
    First item in list = nearest expiry = must be Pre-selected in mobile UI (BRIEF §3).
    """
    from ninja.errors import HttpError
    try:
        p = Product.all_objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise HttpError(404, "الصنف غير موجود")

    # Check if Batch model exists — graceful fallback if not yet migrated
    try:
        from inventory.models import Batch
        batches = Batch.objects.filter(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity__gt=0,
        ).order_by("expiry_date")  # FEFO: nearest expiry FIRST

        warning_date = (date.today() + timedelta(days=30)).isoformat()
        result = []
        for b in batches:
            result.append(BatchOut(
                id=b.id,
                lot_number=b.lot_number,
                expiry_date=b.expiry_date.isoformat() if hasattr(b.expiry_date, "isoformat") else str(b.expiry_date),
                quantity=b.quantity,
                is_expiring_soon=str(b.expiry_date) <= warning_date,
            ))
    except ImportError:
        result = []

    return BatchListResponse(product_id=product_id, batches=result)


@router.get("/{product_id}/serials/", response=list[SerialOut], auth=jwt_auth)
def get_available_serials(request, product_id: int, warehouse_id: int = Query(...)):
    """Available serial units for SERIAL-type products (BRIEF §3)."""
    try:
        from inventory.models import SerialUnit
        serials = SerialUnit.objects.filter(
            product_id=product_id,
            warehouse_id=warehouse_id,
            status="AVAILABLE",
        ).order_by("serial_number")
        return [SerialOut(id=s.id, serial_number=s.serial_number, status=s.status, notes=s.notes) for s in serials]
    except Exception:
        return []
