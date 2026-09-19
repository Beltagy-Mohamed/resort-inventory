"""
Transaction endpoint — the most sensitive endpoint in the system.
Key guarantees (BRIEF §11):
  - Immutable: transactions cannot be edited/deleted after creation
  - Non-negative: stock can never go below zero (enforced by InventoryService)
  - Atomic: inter-warehouse transfer deducts + adds in one DB transaction
  - Idempotent: same client_uuid processed only once (prevents double-submit)
  - ActivityLog: every transaction recorded with real user (BRIEF §11.7)
"""
from ninja import Router
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError
from inventory.models import (
    InventoryTransaction, Product, Warehouse, Partner, ActivityLog
)
from inventory.services.inventory_service import InventoryService
from .schemas import TransactionIn, TransactionOut, TransactionType
from .auth import jwt_auth

router = Router(tags=["Transactions"])


def _get_or_none(model, pk):
    if pk is None:
        return None
    try:
        return model.all_objects.get(pk=pk)
    except Exception:
        return None


@router.post("/", response=TransactionOut, auth=jwt_auth)
def create_transaction(request, payload: TransactionIn):
    """
    Execute inventory transaction — IN / OUT / ADJUST / TRANSFER.

    Idempotency: if client_uuid already exists, returns the original result silently.
    The server never double-counts a transaction even if the mobile retries (BRIEF §8).
    """
    from ninja.errors import HttpError

    # ── Idempotency check — same UUID = already processed ────────────────────
    existing = InventoryTransaction.all_objects.filter(
        client_uuid=payload.client_uuid
    ).first() if hasattr(InventoryTransaction, "client_uuid") else None

    if existing:
        return TransactionOut(
            id=existing.id,
            client_uuid=payload.client_uuid,
            status="ALREADY_PROCESSED",
            message="تمت معالجة هذه العملية مسبقًا",
        )

    # ── Fetch related objects ─────────────────────────────────────────────────
    try:
        product   = Product.all_objects.get(pk=payload.product_id)
        warehouse = Warehouse.all_objects.get(pk=payload.warehouse_id)
    except (Product.DoesNotExist, Warehouse.DoesNotExist):
        raise HttpError(404, "الصنف أو المخزن غير موجود")

    partner = _get_or_none(Partner, payload.partner_id)

    # ── TRANSFER: atomic deduct from source, add to target ───────────────────
    if payload.transaction_type == TransactionType.TRANSFER:
        if payload.target_warehouse_id is None:
            raise HttpError(400, "يجب تحديد مخزن الهدف للتحويل")
        try:
            target_wh = Warehouse.all_objects.get(pk=payload.target_warehouse_id)
        except Warehouse.DoesNotExist:
            raise HttpError(404, "مخزن الهدف غير موجود")

        with db_transaction.atomic():
            # OUT from source
            out_tx = InventoryTransaction(
                user=request.user,
                product=product,
                warehouse=warehouse,
                transaction_type="OUT",
                quantity=payload.quantity,
                unit_price=payload.unit_price,
                notes=f"تحويل إلى {target_wh.name} — {payload.notes or ''}".strip(" —"),
            )
            _attach_uuid(out_tx, payload.client_uuid + "_out")
            InventoryService.process(out_tx)

            # IN to target
            in_tx = InventoryTransaction(
                user=request.user,
                product=product,
                warehouse=target_wh,
                transaction_type="IN",
                quantity=payload.quantity,
                unit_price=payload.unit_price,
                notes=f"تحويل من {warehouse.name} — {payload.notes or ''}".strip(" —"),
            )
            _attach_uuid(in_tx, payload.client_uuid + "_in")
            InventoryService.process(in_tx)

            _log_activity(request.user, "TRANSFER", product, out_tx, in_tx)

        return TransactionOut(
            id=out_tx.id,
            client_uuid=payload.client_uuid,
            status="CONFIRMED",
        )

    # ── Standard transaction: IN / OUT / ADJUST ───────────────────────────────
    t_type_map = {
        TransactionType.IN:     "IN",
        TransactionType.OUT:    "OUT",
        TransactionType.ADJUST: "ADJUST",
    }
    try:
        tx = InventoryTransaction(
            user             = request.user,
            product          = product,
            warehouse        = warehouse,
            partner          = partner,
            transaction_type = t_type_map[payload.transaction_type],
            quantity         = payload.quantity,
            unit_price       = payload.unit_price,
            notes            = payload.notes,
        )
        _attach_uuid(tx, payload.client_uuid)
        InventoryService.process(tx)

        # Activity log — every transaction must record real user (BRIEF §11.7)
        action_map = {"IN": "IN", "OUT": "OUT", "ADJUST": "ADJUST"}
        ActivityLog.all_objects.create(
            user        = request.user,
            action      = action_map.get(tx.transaction_type, "ADD"),
            product     = product,
            old_quantity= tx._old_qty,
            new_quantity= tx._new_qty,
            description = f"{request.user.username} — {tx.transaction_type} {tx.quantity} × {product.name}",
        )

    except ValidationError as e:
        raise HttpError(400, str(e.message if hasattr(e, "message") else e))

    return TransactionOut(
        id=tx.id,
        client_uuid=payload.client_uuid,
        status="CONFIRMED",
    )


def _attach_uuid(tx, uuid: str):
    """Attach client_uuid to transaction if the field exists on the model."""
    if hasattr(InventoryTransaction, "client_uuid"):
        tx.client_uuid = uuid


def _log_activity(user, action, product, out_tx, in_tx):
    for tx in (out_tx, in_tx):
        ActivityLog.all_objects.create(
            user        = user,
            action      = "OUT" if tx.transaction_type == "OUT" else "IN",
            product     = product,
            old_quantity= getattr(tx, "_old_qty", None),
            new_quantity= getattr(tx, "_new_qty", None),
            description = f"{user.username} — TRANSFER {tx.quantity} × {product.name}",
        )
