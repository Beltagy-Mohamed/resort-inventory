from django.db.models import Q, F, Sum, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
import logging
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from inventory.decorators import leadership_required, leader_or_leaderstaff_required
from inventory.forms import ProductForm
from inventory.models import ActivityLog, InventoryTransaction, LeadershipAccessLog, Product, Warehouse
from inventory.utils import get_client_ip, get_period_date_range
from django.db.models import Sum, Q

logger = logging.getLogger("inventory.leadership")

def log_leadership_access(request, action, product=None):
    LeadershipAccessLog.objects.create(
        user=request.user,
        action=action,
        product=product,
        ip_address=get_client_ip(request)
    )

@leader_or_leaderstaff_required
def leadership_items_list(request):
    log_leadership_access(request, "VIEW_LIST")
    products = Product.all_objects.select_related("supplier").filter(is_leadership_restricted=True).order_by("-id")
    search = request.GET.get("search", "")
    warehouse_id = request.GET.get("warehouse")
    
    from django.db.models import Subquery, OuterRef

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
        products = products.filter(name__icontains=search)

    # Period filtering
    period = request.GET.get('period')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    period_data = None
    if period:
        start_dt, end_dt = get_period_date_range(period, start_date, end_date)
        if start_dt and end_dt:
            period_data = {}
            for p in products:
                # Opening balance: sum of IN minus sum of OUT before start_dt
                past_in = InventoryTransaction.objects.filter(product=p, transaction_type='IN', created_at__lt=start_dt).aggregate(s=Sum('quantity'))['s'] or 0
                past_out = InventoryTransaction.objects.filter(product=p, transaction_type='OUT', created_at__lt=start_dt).aggregate(s=Sum('quantity'))['s'] or 0
                opening = past_in - past_out
                
                # Period transactions
                added = InventoryTransaction.objects.filter(product=p, transaction_type='IN', created_at__range=(start_dt, end_dt)).aggregate(s=Sum('quantity'))['s'] or 0
                issued = InventoryTransaction.objects.filter(product=p, transaction_type='OUT', created_at__range=(start_dt, end_dt)).aggregate(s=Sum('quantity'))['s'] or 0
                
                closing = opening + added - issued
                period_data[p.id] = {
                    'opening': opening,
                    'added': added,
                    'issued': issued,
                    'closing': closing
                }


    if request.GET.get("export") == "xlsx":
        import openpyxl
        from django.http import HttpResponse
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "المقرات والقيادات"
        
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
            row = [
                p.barcode or "",
                p.name,
                p.target_quantity,
                getattr(p, 'total_supplied', 0),
                getattr(p, 'remaining_target', 0),
                "مكتمل" if getattr(p, 'remaining_target', 0) <= 0 else ("لم يورد" if getattr(p, 'total_supplied', 0) == 0 else "جاري التوريد"),
                p.supplier.name if p.supplier else "",
            ]
            ws.append(row)
            
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="leadership_items.xlsx"'
        wb.save(response)
        return response

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Build quantity log map for leader products
    page_product_ids = [p.id for p in page_obj]
    all_logs = (
        ActivityLog.all_objects
        .filter(product_id__in=page_product_ids, new_quantity__isnull=False)
        .order_by('product_id', '-created_at')
    )
    quantity_log_map = {}
    for log in all_logs:
        if log.product_id not in quantity_log_map:
            quantity_log_map[log.product_id] = log

    return render(request, "products/list.html", {
        "page_obj": page_obj,
        "search": search,
        "is_leadership": True,
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "period_data": period_data,
        "quantity_log_map": quantity_log_map,
        "warehouses": Warehouse.objects.all(),
        "warehouse_id": warehouse_id,
    })

@leader_or_leaderstaff_required
def leadership_item_add(request):
    log_leadership_access(request, "ADD_ITEM")
    if request.method == "POST":
        form = ProductForm(request.POST, is_leader=True)
        if form.is_valid():
            with transaction.atomic():
                product = form.save(commit=False)
                # We no longer force is_leadership_restricted=True here; we respect the form's checkbox
                product.save()
                
                warehouse = form.cleaned_data.get('warehouse')
                quantity = form.cleaned_data.get('quantity', 0)
                
                if warehouse and quantity > 0:
                    trans = InventoryTransaction(
                        product=product,
                        warehouse=warehouse,
                        transaction_type='IN',
                        quantity=quantity,
                        unit_price=product.cost_price,
                        notes='رصيد افتتاحي (مضاف من واجهة القائد)'
                    )
                    from inventory.services.inventory_service import InventoryService
                    InventoryService.process(trans)

            messages.success(request, "تمت إضافة الصنف بنجاح.")
            return redirect("leadership_items_list")
    else:
        form = ProductForm(initial={'is_leadership_restricted': True}, is_leader=True)
    
    return render(request, "products/add.html", {"form": form, "is_leadership_form": True})

@leader_or_leaderstaff_required
def leadership_item_edit(request, pk):
    product = get_object_or_404(Product.all_objects, pk=pk, is_leadership_restricted=True)
    log_leadership_access(request, "EDIT_ITEM", product)
    
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product, is_leader=True)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل صنف القائد بنجاح.")
            return redirect("leadership_items_list")
    else:
        form = ProductForm(instance=product, is_leader=True)
    
    return render(request, "products/edit.html", {"form": form, "is_leadership_form": True})

@leader_or_leaderstaff_required
def leadership_item_delete(request, pk):
    product = get_object_or_404(Product.all_objects, pk=pk, is_leadership_restricted=True)
    log_leadership_access(request, "DELETE_ITEM", product)
    
    if request.method == "POST":
        try:
            product.delete()
            messages.success(request, "تم حذف صنف القائد بنجاح.")
        except ProtectedError:
            messages.error(request, "لا يمكن حذف الصنف لارتباطه بحركات مخزنية.")
        return redirect("leadership_items_list")
    
    return render(request, "products/delete.html", {"product": product, "is_leadership_form": True})

@leader_or_leaderstaff_required
def leadership_item_detail(request, pk):
    product = get_object_or_404(Product.all_objects, pk=pk, is_leadership_restricted=True)
    log_leadership_access(request, "VIEW_DETAIL", product)
    
    return render(request, "products/detail.html", {"product": product, "is_leadership_form": True})

@leader_or_leaderstaff_required
def leadership_dashboard(request):
    log_leadership_access(request, "VIEW_DASHBOARD")
    products = Product.all_objects.select_related("supplier").filter(is_leadership_restricted=True)
    from django.db.models import Sum, F
    total_stock = products.aggregate(Sum('quantity'))['quantity__sum'] or 0
    low_stock = products.filter(quantity__lte=F('minimum_stock'), quantity__gt=0).count()
    out_of_stock = products.filter(quantity=0).count()
    recent_transactions = InventoryTransaction.objects.filter(product__is_leadership_restricted=True).order_by('-created_at')[:10]

    return render(request, "leadership/dashboard.html", {
        "total_products": products.count(),
        "total_stock": total_stock,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "recent_transactions": recent_transactions,
    })

@leader_or_leaderstaff_required
def leadership_warehouses_list(request):
    log_leadership_access(request, "VIEW_WAREHOUSES")
    warehouses = Warehouse.all_objects.filter(is_leader_only=True)
    return render(request, "leadership/warehouses.html", {"warehouses": warehouses})

@leader_or_leaderstaff_required
def leadership_transactions_list(request):
    log_leadership_access(request, "VIEW_TRANSACTIONS")
    
    # Use all_objects to bypass the PublicManager filter
    transactions = InventoryTransaction.all_objects.filter(product__is_leadership_restricted=True)
    
    search = request.GET.get("search", "")
    if search:
        transactions = transactions.filter(
            Q(product__name__icontains=search) | Q(product__barcode__icontains=search)
        )
        
    transactions = transactions.select_related("product", "warehouse", "partner").order_by("-created_at")
    
    paginator = Paginator(transactions, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "transactions/list.html", {
        "page_obj": page_obj,
        "search": search,
        "is_leadership": True
    })

@leader_or_leaderstaff_required
def leadership_report_print(request):
    log_leadership_access(request, "PRINT_REPORT")
    products = Product.all_objects.select_related("supplier").filter(is_leadership_restricted=True).order_by('category', 'name')
    
    try:
        from weasyprint import HTML
        from django.template.loader import render_to_string
        html_string = render_to_string('reports/print_template.html', {'products': products})
        pdf_file = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="leadership_report.pdf"'
        return response
    except Exception as e:
        logger.error(f"WeasyPrint error: {e}")
        messages.error(request, "عذراً، نظام الطباعة غير متوفر حالياً بسبب نقص بعض المكتبات على نظام ويندوز. يرجى استخدام متصفحك لطباعة الشاشة.")
        return redirect("leadership_dashboard")


@leader_or_leaderstaff_required
def leadership_items_export(request):
    import openpyxl
    from django.http import HttpResponse
    
    products = Product.all_objects.select_related("supplier").filter(is_leadership_restricted=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leadership Items"
    ws.append(["الكود", "الاسم", "الكمية", "السعر", "الفئة"])
    
    for p in products:
        ws.append([p.id, p.name, p.quantity, p.selling_price, p.category.name if p.category else ""])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=leadership_items.xlsx'
    wb.save(response)
    return response
