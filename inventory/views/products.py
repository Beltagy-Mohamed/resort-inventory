from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from django.db.models import Q, F, Sum, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from ..forms import ProductForm
from ..models import Product, ActivityLog, Category, Color, Size, InventoryTransaction
@login_required
@permission_required("inventory.view_product", raise_exception=True)
def products_list(request):
    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    category_id = request.GET.get("category", "")
    color_id = request.GET.get("color", "")
    size_id = request.GET.get("size", "")
    period = request.GET.get("period", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    warehouse_id = request.GET.get("warehouse", "")

    products = Product.objects.select_related("category", "color", "size")
    
    from inventory.models import InventoryTransaction, Warehouse

    if warehouse_id:
        supplied_expr = Coalesce(Sum('transactions__quantity', filter=Q(transactions__transaction_type='IN', transactions__warehouse_id=warehouse_id)), 0)
        products = products.filter(stocks__warehouse_id=warehouse_id).annotate(
            display_quantity=Coalesce(Sum('stocks__quantity', filter=Q(stocks__warehouse_id=warehouse_id)), 0),
            total_supplied=supplied_expr,
            remaining_target=F('target_quantity') - supplied_expr
        )
    else:
        supplied_expr = Coalesce(Sum('transactions__quantity', filter=Q(transactions__transaction_type='IN')), 0)
        products = products.annotate(
            display_quantity=F('quantity'),
            total_supplied=supplied_expr,
            remaining_target=F('target_quantity') - supplied_expr
        )

    if search:
        products = products.filter(Q(name__icontains=search) | Q(barcode__icontains=search))

    if category_id:
        products = products.filter(category_id=category_id)
    if color_id:
        products = products.filter(color_id=color_id)
    if size_id:
        products = products.filter(size_id=size_id)

    if status == "available":
        products = products.filter(display_quantity__gt=F("minimum_stock"))
    elif status == "low":
        products = products.filter(display_quantity__gt=0, display_quantity__lte=F("minimum_stock"))
    elif status == "out":
        products = products.filter(display_quantity=0)

    products = products.order_by("-id").distinct()
    
    period_data = None
    if period:
        start_dt, end_dt = get_period_date_range(period, start_date, end_date)
        if start_dt and end_dt:
            period_data = {}
            for p in products:
                wh_q = Q(warehouse_id=warehouse_id) if warehouse_id else Q()
                past_in = InventoryTransaction.objects.filter(wh_q, product=p, transaction_type='IN', created_at__lt=start_dt).aggregate(s=Sum('quantity'))['s'] or 0
                past_out = InventoryTransaction.objects.filter(wh_q, product=p, transaction_type='OUT', created_at__lt=start_dt).aggregate(s=Sum('quantity'))['s'] or 0
                opening = past_in - past_out
                
                added = InventoryTransaction.objects.filter(wh_q, product=p, transaction_type='IN', created_at__range=(start_dt, end_dt)).aggregate(s=Sum('quantity'))['s'] or 0
                issued = InventoryTransaction.objects.filter(wh_q, product=p, transaction_type='OUT', created_at__range=(start_dt, end_dt)).aggregate(s=Sum('quantity'))['s'] or 0
                
                period_data[p.id] = {
                    'opening': opening,
                    'added': added,
                    'issued': issued,
                    'closing': opening + added - issued
                }

    if request.GET.get("export") == "xlsx":
        import openpyxl
        from django.http import HttpResponse
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "المنتجات"
        
        headers = [
            "الكود",
            "اسم الصنف",
            "التنميط",
            "ما تم توريده",
            "المتبقي",
            "الحالة",
            "اسم الشركة",
        ]
        ws.append(headers)
        
        for p in products:
            ws.append([
                p.barcode or "",
                p.name,
                p.target_quantity,
                getattr(p, 'total_supplied', 0),
                getattr(p, 'remaining_target', 0),
                "مكتمل" if getattr(p, 'remaining_target', 0) <= 0 else ("لم يورد" if getattr(p, 'total_supplied', 0) == 0 else "جاري التوريد"),
                p.supplier.name if p.supplier else "",
            ])
            
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="products.xlsx"'
        wb.save(response)
        return response

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Build a dict: product_id â†’ last ActivityLog with quantity info
    page_product_ids = [p.id for p in page_obj]
    last_logs = (
        ActivityLog.objects
        .filter(product_id__in=page_product_ids, new_quantity__isnull=False)
        .order_by('product_id', '-created_at')
        .distinct('product_id')
    )
    # Fallback for SQLite (no DISTINCT ON support): use Python groupby
    from itertools import groupby as _groupby
    try:
        quantity_log_map = {log.product_id: log for log in last_logs}
    except Exception:
        all_logs = (
            ActivityLog.objects
            .filter(product_id__in=page_product_ids, new_quantity__isnull=False)
            .order_by('product_id', '-created_at')
        )
        quantity_log_map = {}
        for log in all_logs:
            if log.product_id not in quantity_log_map:
                quantity_log_map[log.product_id] = log

    return render(
        request,
        "products/list.html",
        {
            "page_obj": page_obj,
            "search": search,
            "status": status,
            "category_id": category_id,
            "color_id": color_id,
            "size_id": size_id,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "period_data": period_data,
            "quantity_log_map": quantity_log_map,
            "categories": Category.objects.all(),
            "colors": Color.objects.all(),
            "sizes": Size.objects.all(),
            "warehouses": Warehouse.objects.all(),
            "warehouse_id": warehouse_id
        }
    )
    
    
@login_required
@permission_required("inventory.add_product", raise_exception=True)
def add_product(request):
    from inventory.decorators import is_the_leader
    is_leader = is_the_leader(request.user)

    if request.method == "POST":

        form = ProductForm(request.POST, is_leader=is_leader)

        if form.is_valid():

            product = form.save(commit=False)

            product.save()
            
            # Create initial stock transaction if quantity > 0
            if product.quantity > 0:
                from inventory.models import InventoryTransaction
                trans = InventoryTransaction(
                    product=product,
                    transaction_type="IN",
                    quantity=product.quantity,
                    notes="رصيد افتتاحي"
                )
                InventoryService.process(trans)

            messages.success(
            request,
            "ØªÙ… Ø¥Ø¶Ø§ÙØ© Ø§Ù„Ù…Ù†ØªØ¬ Ø¨Ù†Ø¬Ø§Ø­."
            )
            return redirect("products_list")

    else:

        form = ProductForm(is_leader=is_leader)

    return render(
        request,
        "products/add.html",
        {
            "form": form
        }
    )


@login_required
@permission_required("inventory.change_product", raise_exception=True)
def edit_product(request, pk):
    from inventory.decorators import is_the_leader
    is_leader = is_the_leader(request.user)
    
    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            instance=product,
            is_leader=is_leader
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "ØªÙ… ØªØ¹Ø¯ÙŠÙ„ Ø§Ù„Ù…Ù†ØªØ¬ Ø¨Ù†Ø¬Ø§Ø­."
            )

            return redirect("products_list")

    else:

        form = ProductForm(instance=product, is_leader=is_leader)

    return render(
        request,
        "products/edit.html",
        {
            "form": form,
            "product": product
        }
    )    
    
@login_required
@permission_required("inventory.delete_product", raise_exception=True)
def delete_product(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
       
        try:
            product.delete()
        except ProtectedError:
            messages.error(
                request,
                "Ù„Ø§ ÙŠÙ…ÙƒÙ† Ø­Ø°Ù Ù…Ù†ØªØ¬ Ù„Ù‡ Ø­Ø±ÙƒØ§Øª Ù…Ø®Ø²Ù†ÙŠØ©. Ø§Ø­ØªÙØ¸ Ø¨Ù‡ Ù„Ù„Ø£Ø±Ø´ÙØ© Ø§Ù„ØªØ§Ø±ÙŠØ®ÙŠØ©.",
            )
        else:
            messages.success(request, "ØªÙ… Ø­Ø°Ù Ø§Ù„Ù…Ù†ØªØ¬ Ø¨Ù†Ø¬Ø§Ø­.")

        return redirect("products_list")

    return render(
        request,
        "products/delete.html",
        {
            "product": product
        }
    )
    
@login_required
@permission_required("inventory.view_product", raise_exception=True)
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Calculate stock summary
    from django.db.models import Sum
    all_transactions = product.transactions.all()
    
    basic_qty = all_transactions.filter(notes__contains='Ø±ØµÙŠØ¯ Ø§ÙØªØªØ§Ø­ÙŠ').aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    added_qty = all_transactions.filter(transaction_type='IN').exclude(notes__contains='Ø±ØµÙŠØ¯ Ø§ÙØªØªØ§Ø­ÙŠ').aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    out_qty = all_transactions.filter(transaction_type='OUT').aggregate(Sum('quantity'))['quantity__sum'] or 0

    transactions = all_transactions[:10]

    return render(
        request,
        "products/detail.html",
        {
            "product": product,
            "transactions": transactions,
            "basic_qty": basic_qty,
            "added_qty": added_qty,
            "out_qty": out_qty,
        }
    )


@login_required
@permission_required("inventory.view_product", raise_exception=True)
def low_stock_products(request):

    products = Product.objects.filter(
        quantity__lte=F("minimum_stock")
    ).order_by("quantity")

    return render(
        request,
        "products/low_stock.html",
        {
            "products": products
        }
    )    

