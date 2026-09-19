"""Warehouse listing — respects PublicWarehouseManager (hides is_leader_only=True for normal users)."""
from ninja import Router
from inventory.models import Warehouse
from inventory.decorators import is_the_leader
from .schemas import WarehouseOut
from .auth import jwt_auth

router = Router(tags=["Warehouses"])


@router.get("/", response=list[WarehouseOut], auth=jwt_auth)
def list_warehouses(request):
    """
    Lists warehouses visible to the current user.
    PublicWarehouseManager automatically filters is_leader_only=True for normal users.
    Leaders see all warehouses via all_objects.
    """
    if is_the_leader(request.user):
        qs = Warehouse.all_objects.all()
    else:
        qs = Warehouse.objects.all()   # PublicWarehouseManager excludes leader warehouses
    return [WarehouseOut(id=w.id, name=w.name, location=w.location, manager=w.manager) for w in qs]
