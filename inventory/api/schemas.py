"""
Pydantic v2 schemas for the Django Ninja API (Mobile endpoints).
All financial fields use Decimal — Float is banned (BRIEF §11.4).
barcode is intentionally ABSENT from all schemas (BRIEF §0.1).
"""
from __future__ import annotations
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, field_validator
from enum import Enum


# ─── Auth ────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access:  str
    refresh: str

class RefreshRequest(BaseModel):
    refresh: str

class RefreshResponse(BaseModel):
    access: str


# ─── Tracking types ───────────────────────────────────────────────────────────

class TrackingType(str, Enum):
    NONE         = "NONE"
    LOT          = "LOT"
    BATCH_EXPIRY = "BATCH_EXPIRY"
    SERIAL       = "SERIAL"


# ─── Products ─────────────────────────────────────────────────────────────────

class ProductSearchItem(BaseModel):
    """
    Single-line render rule — all distinguishing traits (BRIEF §11.11).
    name + product_code + color + size + warehouse_stock
    NOTE: barcode intentionally absent (BRIEF §0.1)
    """
    id             : int
    name           : str
    product_code   : str
    color          : Optional[str]
    size           : Optional[str]
    warehouse_stock: int
    tracking_type  : TrackingType

class ProductSearchResponse(BaseModel):
    count  : int
    next   : Optional[str]
    results: List[ProductSearchItem]

class WarehouseStockItem(BaseModel):
    warehouse_id  : int
    warehouse_name: str
    quantity      : int

class ProductDetail(BaseModel):
    id           : int
    name         : str
    product_code : str
    category     : Optional[str]
    color        : Optional[str]
    size         : Optional[str]
    cost_price   : Decimal
    selling_price: Decimal
    quantity     : int
    minimum_stock: int
    tracking_type: TrackingType
    is_archived  : bool
    is_leader_only: bool
    stock_by_warehouse: List[WarehouseStockItem] = []


# ─── Warehouses ───────────────────────────────────────────────────────────────

class WarehouseOut(BaseModel):
    id      : int
    name    : str
    location: Optional[str]
    manager : Optional[str]


# ─── Batches (BATCH_EXPIRY) ───────────────────────────────────────────────────

class BatchOut(BaseModel):
    """
    FEFO: First Expired First Out.
    Results are ordered by expiry_date ASC — nearest expiry first.
    The first item in the list should be Pre-selected in the mobile UI.
    """
    id         : int
    lot_number : str
    expiry_date: str   # ISO date string: "2026-12-31"
    quantity   : int
    is_expiring_soon: bool  # True if within 30 days

class BatchListResponse(BaseModel):
    product_id: int
    batches   : List[BatchOut]  # Ordered: nearest expiry FIRST


# ─── Serials (SERIAL) ─────────────────────────────────────────────────────────

class SerialStatus(str, Enum):
    AVAILABLE      = "AVAILABLE"
    ISSUED         = "ISSUED"
    MAINTENANCE    = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class SerialOut(BaseModel):
    id           : int
    serial_number: str
    status       : SerialStatus
    notes        : Optional[str]


# ─── Transactions ─────────────────────────────────────────────────────────────

class TransactionType(str, Enum):
    IN       = "IN"
    OUT      = "OUT"
    ADJUST   = "ADJUST"
    TRANSFER = "TRANSFER"

class TransactionIn(BaseModel):
    """
    Mobile sends a Delta (TransactionRequest), never a final quantity.
    client_uuid is a UUIDv7 idempotency key — server processes each UUID once only.
    BRIEF §8, §0.2 — Last Write Wins is BANNED.
    """
    client_uuid      : str    # UUIDv7
    product_id       : int
    warehouse_id     : int
    transaction_type : TransactionType
    quantity         : int
    unit_price       : Decimal = Decimal("0.00")
    partner_id       : Optional[int]  = None
    notes            : Optional[str]  = None
    # BATCH_EXPIRY fields
    lot_number       : Optional[str]  = None
    expiry_date      : Optional[str]  = None
    batch_id         : Optional[int]  = None
    # SERIAL field
    serial_number    : Optional[str]  = None
    # TRANSFER extra field
    target_warehouse_id: Optional[int] = None

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v

class TransactionOut(BaseModel):
    id          : int
    client_uuid : str
    status      : str
    message     : str = "تمت العملية بنجاح"


# ─── Sync ─────────────────────────────────────────────────────────────────────

class DeltaResponse(BaseModel):
    products     : List[ProductDetail]
    last_synced_at: int   # epoch millis UTC


# ─── Leadership ───────────────────────────────────────────────────────────────

class LeaderProductOut(BaseModel):
    id           : int
    name         : str
    product_code : str
    category     : Optional[str]
    color        : Optional[str]
    size         : Optional[str]
    cost_price   : Decimal
    selling_price: Decimal
    quantity     : int
    tracking_type: TrackingType

class LeaderStatsOut(BaseModel):
    total_products    : int
    total_value       : Decimal
    low_stock_count   : int
    today_transactions: int
