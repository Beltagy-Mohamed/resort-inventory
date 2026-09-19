"""
Django Ninja API — assembles all routers.
Base URL: /api/v1/
Versioning via URL prefix — no breaking changes without incrementing the version.

BRIEF §6: 9 endpoints documented. All require JWT auth except /auth/token/ and /auth/token/refresh/.
"""
from ninja import NinjaAPI
from ninja.errors import HttpError
from django.http import JsonResponse
from .auth        import router as auth_router
from .products    import router as products_router
from .transactions import router as transactions_router
from .warehouses  import router as warehouses_router
from .sync        import router as sync_router
from .leadership  import router as leadership_router

api = NinjaAPI(
    title       = "Resort Inventory API",
    version     = "1.0",
    description = "Mobile API for Resort Inventory Management System",
    docs_url    = "/docs",   # Swagger UI at /api/v1/docs
)

# ── Mount routers at paths matching BRIEF §6 ─────────────────────────────────
api.add_router("/auth/",         auth_router)
api.add_router("/products/",     products_router)
api.add_router("/transactions/", transactions_router)
api.add_router("/warehouses/",   warehouses_router)
api.add_router("/sync/",         sync_router)
api.add_router("/leadership/",   leadership_router)


# ── Global error handlers ────────────────────────────────────────────────────

@api.exception_handler(HttpError)
def handle_http_error(request, exc: HttpError):
    return api.create_response(
        request,
        {"detail": exc.message},
        status=exc.status_code,
    )

@api.exception_handler(Exception)
def handle_generic_error(request, exc: Exception):
    # Never leak stack traces in production
    import logging
    logging.getLogger(__name__).exception("Unhandled API error")
    return api.create_response(request, {"detail": "حدث خطأ داخلي"}, status=500)
