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

    transactions = InventoryTransaction.objects.select_related(
        "product"
    )

    if search:

        transactions = transactions.filter(

            Q(product__name__icontains=search) |
            Q(product__product_code__icontains=search)

        )

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
        
    if month_filter:
        try:
            year, month = month_filter.split("-")
            transactions = transactions.filter(created_at__year=year, created_at__month=month)
        except ValueError:
            pass

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
            "month_filter": month_filter,
        }

    )


@login_required
@permission_required("inventory.add_inventorytransaction", raise_exception=True)
def add_transaction(request):

    if request.method == "POST":

        form = InventoryTransactionForm(request.POST)

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

                    product.product_code

                )

            except ValidationError as e:

                messages.error(

                    request,

                    e.message

                )

    else:

        form = InventoryTransactionForm()

    return render(

        request,

        "transactions/add.html",

        {

            "form": form

        }

    )