# Inventory System — Source Review / Delivery Copy

**This is NOT a complete, runnable production copy of the project.**
It is a source-review package prepared for evaluation purposes only.
See `PROPRIETARY_LICENSE.txt` for the terms under which this copy is
provided.

## What this copy contains

Nearly the full Django codebase, for review purposes:

- All models, forms, admin config, URL routing
- All views except one deliberately-broken import (see below)
- All templates and static assets (CSS/JS)
- All database migrations
- Two of the four service classes (`barcode_service.py`, `qr_service.py`)
- Deployment reference files (`deploy/`, `DEPLOYMENT.md`) — these
  describe a *generic* deployment process and contain no real
  credentials or server details
- `requirements.txt`
- `.env.example` — placeholder values only, no real secrets

## What was excluded, and why

| Item | Reason for exclusion |
|---|---|
| `db.sqlite3` | Contained real user accounts, a real email address, and password hashes. Never part of a source-review delivery. |
| `media/` (barcodes, QR codes) | Runtime-generated files tied to real product records. Not source code — regenerated automatically by the app once running. |
| `inventory/services/inventory_service.py` | Contains the project's core proprietary business logic (stock-mutation rules, concurrency safety, double-processing prevention). Retained by the copyright holder and **not included** in this copy. |
| `.env` (real file) | N/A — no real `.env` file exists in the source project; only the placeholder `.env.example` is included. |

## Why this project will not run as-is

`inventory/views/transactions.py` still imports
`inventory.services.inventory_service.InventoryService`, which is not
present in this copy. This means:

- The project will **not** start/deploy successfully as a working
  system.
- Specifically, the "add inventory transaction" feature will raise
  `ModuleNotFoundError` at import time.

This is intentional and disclosed here — not a hidden restriction, a
license check, a time bomb, or any other concealed mechanism. It is a
single missing file, clearly marked in the code with a comment at the
import line in `transactions.py`.

Everything else in the codebase is real, complete, and reviewable as-is.

## If you need a working deployment

A complete, deployable version of this system — including the
proprietary service module — is available only under a separate
licensing/delivery agreement with the copyright holder. Contact the
Owner to discuss options.
