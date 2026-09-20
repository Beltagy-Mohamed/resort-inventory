from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, permission_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from ..forms import InventoryTransactionForm
from ..models import InventoryTransaction

# ---------------------------------------------------------------------------
# EXCLUDED FROM THIS DELIVERY COPY
# ---------------------------------------------------------------------------
# `inventory/services/inventory_service.py` (the InventoryService class) has
# been intentionally left out of this source-review package — it contains
# proprietary business logic that the copyright holder has retained.
#
# This import will raise ModuleNotFoundError, and add_transaction() below
# will not run, until that module is supplied separately by the copyright
# holder. This is expected and documented — see README_DELIVERY.md,
# section "What was excluded and why".
# ---------------------------------------------------------------------------


@login_required
@permission_required("inventory.view_inventorytransaction", raise_exception=True)
def transactions_list(request):

    search = request.GET.get("search", "")
    transaction_type = request.GET.get("type", "")
    month_filter = request.GET.get("month_filter", "")
    warehouse_filter = request.GET.get("warehouse", "")

    transactions = InventoryTransaction.objects.select_related(
        "product"
    )

    if search:

        transactions = transactions.filter(

            Q(product__name__icontains=search) |
            Q(product__id__icontains=search)

        )

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    if warehouse_filter:
        transactions = transactions.filter(warehouse_id=warehouse_filter)
        
    year_filter = request.GET.get("year_filter", "")
    
    if month_filter and month_filter.isdigit():
        transactions = transactions.filter(created_at__month=int(month_filter))
    
    if year_filter and year_filter.isdigit():
        transactions = transactions.filter(created_at__year=int(year_filter))

    transactions = transactions.order_by("-created_at")

    paginator = Paginator(
        transactions,
        15
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(

        request,

        "transactions/list.html",

        {
            "page_obj": page_obj,
            "search": search,
            "transaction_type": transaction_type,
            "month_filter": int(month_filter) if month_filter.isdigit() else "",
            "year_filter": int(year_filter) if year_filter.isdigit() else "",
            "months": [(1, "يناير"), (2, "فبراير"), (3, "مارس"), (4, "أبريل"), (5, "مايو"), (6, "يونيو"), (7, "يوليو"), (8, "أغسطس"), (9, "سبتمبر"), (10, "أكتوبر"), (11, "نوفمبر"), (12, "ديسمبر")],
            "years": range(2025, 2035),
            "warehouses": __import__('inventory.models', fromlist=['Warehouse']).Warehouse.objects.all(),
            "warehouse_filter": warehouse_filter,
        }

    )


import json
from ..models import Product

@login_required
@permission_required("inventory.add_inventorytransaction", raise_exception=True)
def add_transaction(request):
    action = request.GET.get("action", "IN").upper()
    if action not in ["IN", "OUT", "ADJUST"]:
        action = "IN"

    from ..models import Partner
    
    if request.method == "POST":
        # Force the transaction type based on the action parameter to ensure data integrity
        post_data = request.POST.copy()
        post_data['transaction_type'] = action
        form = InventoryTransactionForm(post_data, user=request.user)
        
        # Enforce partner type filtering on POST (respecting leader access)
        from inventory.decorators import is_the_leader
        partner_qs = Partner.all_objects if (request.user.is_superuser or is_the_leader(request.user)) else Partner.objects
        if action == "IN":
            form.fields['partner'].queryset = partner_qs.filter(partner_type="SUPPLIER")
        elif action == "OUT":
            form.fields['partner'].queryset = partner_qs.filter(partner_type__in=["CLIENT", "OTHER"])

        if form.is_valid():

            transaction = form.save(commit=False)

            try:

                from ..services.inventory_service import InventoryService

                product = InventoryService.process(transaction)

                messages.success(

                    request,

                    "تم تسجيل الحركة بنجاح."

                )

                return redirect(

                    "product_detail",

                    product.id

                )

            except ValidationError as e:

                messages.error(

                    request,

                    e.message

                )

    else:
        form = InventoryTransactionForm(user=request.user)
        
        # Enforce partner type filtering on GET (respecting leader access)
        from inventory.decorators import is_the_leader
        partner_qs = Partner.all_objects if (request.user.is_superuser or is_the_leader(request.user)) else Partner.objects
        if action == "IN":
            form.fields['partner'].queryset = partner_qs.filter(partner_type="SUPPLIER")
        elif action == "OUT":
            form.fields['partner'].queryset = partner_qs.filter(partner_type__in=["CLIENT", "OTHER"])

    
    # Build product prices JSON for JS autofill — filtered by user role
    from inventory.decorators import is_the_leader as _is_leader
    products_qs = (
        Product.all_objects.filter(is_archived=False)
        if (request.user.is_superuser or _is_leader(request.user))
        else Product.objects.filter(is_archived=False)
    )
    products_data = {
        p.id: {
            "cost_price": float(p.cost_price), 
            "selling_price": float(p.selling_price)
        } for p in products_qs
    }
    
    return render(
        request,
        "transactions/add.html",
        {
            "form": form,
            "action": action,
            "products_data_json": json.dumps(products_data)
        }
    )
