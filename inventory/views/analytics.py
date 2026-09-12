from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from inventory.models import Stock, Warehouse, Partner, InventoryTransaction

@login_required
def warehouse_stock_report(request):
    warehouse_id = request.GET.get("warehouse_id", "")
    
    stocks = Stock.objects.select_related("product", "warehouse").filter(quantity__gt=0)
    
    if warehouse_id:
        stocks = stocks.filter(warehouse_id=warehouse_id)
        
    stocks = stocks.order_by("warehouse__name", "product__name")
    
    context = {
        "stocks": stocks,
        "warehouses": Warehouse.objects.all(),
        "selected_warehouse": int(warehouse_id) if warehouse_id else "",
    }
    return render(request, "reports/warehouse_stock.html", context)


@login_required
def partner_statement_report(request):
    partner_id = request.GET.get("partner_id", "")
    month_filter = request.GET.get("month_filter", "")
    
    transactions = InventoryTransaction.objects.select_related("product", "partner", "warehouse").none()
    
    if partner_id:
        transactions = InventoryTransaction.objects.select_related("product", "partner", "warehouse").filter(partner_id=partner_id)
        
        if month_filter:
            try:
                year, month = month_filter.split("-")
                transactions = transactions.filter(created_at__year=year, created_at__month=month)
            except ValueError:
                pass
                
        transactions = transactions.order_by("-created_at")
        
    context = {
        "transactions": transactions,
        "partners": Partner.objects.all(),
        "selected_partner": int(partner_id) if partner_id else "",
        "month_filter": month_filter,
    }
    return render(request, "reports/partner_statement.html", context)


@login_required
def profit_report(request):
    month_filter = request.GET.get("month_filter", "")
    
    # We only calculate profit on 'OUT' transactions (Sales/Issuance)
    transactions = InventoryTransaction.objects.select_related("product").filter(transaction_type='OUT')
    
    if month_filter:
        try:
            year, month = month_filter.split("-")
            transactions = transactions.filter(created_at__year=year, created_at__month=month)
        except ValueError:
            pass
            
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
        "month_filter": month_filter,
        "total_profit": total_profit,
        "total_sales": total_sales,
        "total_cost": total_cost,
    }
    return render(request, "reports/profit.html", context)
