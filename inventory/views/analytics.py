from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from inventory.models import Stock, Warehouse, Partner, InventoryTransaction

@login_required
@permission_required("inventory.view_inventorytransaction", raise_exception=True)
def warehouse_stock_report(request):
    warehouse_id = request.GET.get("warehouse_id", "")
    
    stocks = Stock.objects.select_related("product", "warehouse").filter(quantity__gt=0)
    
    if warehouse_id and warehouse_id.isdigit():
        stocks = stocks.filter(warehouse_id=warehouse_id)
        
    stocks = stocks.order_by("warehouse__name", "product__name")
    
    context = {
        "stocks": stocks,
        "warehouses": Warehouse.objects.all(),
        "selected_warehouse": int(warehouse_id) if (warehouse_id and warehouse_id.isdigit()) else "",
    }
    return render(request, "reports/warehouse_stock.html", context)


@login_required
@permission_required("inventory.view_inventorytransaction", raise_exception=True)
def partner_statement_report(request):
    partner_id = request.GET.get("partner_id", "")
    month_filter = request.GET.get("month_filter", "")
    warehouse_filter = request.GET.get("warehouse", "")
    
    transactions = InventoryTransaction.objects.select_related("product", "partner", "warehouse").none()
    
    year_filter = request.GET.get("year_filter", "")
    
    if partner_id and partner_id.isdigit():
        transactions = InventoryTransaction.objects.select_related("product", "partner", "warehouse").filter(partner_id=partner_id)
        if month_filter and month_filter.isdigit():
            transactions = transactions.filter(created_at__month=int(month_filter))
        if year_filter and year_filter.isdigit():
            transactions = transactions.filter(created_at__year=int(year_filter))
                
        transactions = transactions.order_by("-created_at")
        
    context = {
        "transactions": transactions,
        "partners": Partner.objects.all(),
        "selected_partner": int(partner_id) if (partner_id and partner_id.isdigit()) else "",
        "month_filter": int(month_filter) if month_filter.isdigit() else "",
        "warehouse_filter": warehouse_filter,
        "warehouses": Warehouse.objects.all(),
        "year_filter": int(year_filter) if year_filter.isdigit() else "",
        "months": [(1, "يناير"), (2, "فبراير"), (3, "مارس"), (4, "أبريل"), (5, "مايو"), (6, "يونيو"), (7, "يوليو"), (8, "أغسطس"), (9, "سبتمبر"), (10, "أكتوبر"), (11, "نوفمبر"), (12, "ديسمبر")],
        "years": range(2025, 2035),
    }
    return render(request, "reports/partner_statement.html", context)


@login_required
@permission_required("inventory.view_inventorytransaction", raise_exception=True)
def profit_report(request):
    month_filter = request.GET.get("month_filter", "")
    warehouse_filter = request.GET.get("warehouse", "")
    
    # We only calculate profit on 'OUT' transactions (Sales/Issuance)
    transactions = InventoryTransaction.objects.select_related("product").filter(transaction_type='OUT')
    
    year_filter = request.GET.get("year_filter", "")
    if month_filter and month_filter.isdigit():
        transactions = transactions.filter(created_at__month=int(month_filter))
    if year_filter and year_filter.isdigit():
        transactions = transactions.filter(created_at__year=int(year_filter))
    if warehouse_filter and warehouse_filter.isdigit():
        transactions = transactions.filter(warehouse_id=warehouse_filter)
            
    # Calculate Profit: (unit_price - cost_price) * quantity
    transactions = transactions.annotate(
        profit=ExpressionWrapper(
            (F('unit_price') - F('product__cost_price')) * F('quantity'),
            output_field=DecimalField()
        )
    ).order_by("-created_at")
    
    total_profit = transactions.aggregate(total=Sum('profit'))['total'] or 0
    total_sales = transactions.aggregate(total=Sum(F('unit_price') * F('quantity')))['total'] or 0
    total_cost = transactions.aggregate(total=Sum(F('product__cost_price') * F('quantity')))['total'] or 0
    
    context = {
        "transactions": transactions,
        "warehouses": Warehouse.objects.order_by("name"),
        "warehouse_filter": warehouse_filter,
        "month_filter": int(month_filter) if month_filter.isdigit() else "",
        "warehouse_filter": warehouse_filter,
        "warehouses": Warehouse.objects.all(),
        "year_filter": int(year_filter) if year_filter.isdigit() else "",
        "months": [(1, "يناير"), (2, "فبراير"), (3, "مارس"), (4, "أبريل"), (5, "مايو"), (6, "يونيو"), (7, "يوليو"), (8, "أغسطس"), (9, "سبتمبر"), (10, "أكتوبر"), (11, "نوفمبر"), (12, "ديسمبر")],
        "years": range(2025, 2035),
        "total_profit": total_profit,
        "total_sales": total_sales,
        "total_cost": total_cost,
    }
    return render(request, "reports/profit.html", context)
