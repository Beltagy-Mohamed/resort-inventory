from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from django.db.models import Q, F
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

    products = Product.objects.select_related("category", "color", "size")

    if search:
        products = products.filter(Q(name__icontains=search) | Q(barcode__icontains=search))

    if category_id:
        products = products.filter(category_id=category_id)
    if color_id:
        products = products.filter(color_id=color_id)
    if size_id:
        products = products.filter(size_id=size_id)

    if status == "available":
        products = products.filter(quantity__gt=F("minimum_stock"))
    elif status == "low":
        products = products.filter(quantity__gt=0, quantity__lte=F("minimum_stock"))
    elif status == "out":
        products = products.filter(quantity=0)

    products = products.order_by("-id")
    
    period_data = None
    if period:
        start_dt, end_dt = get_period_date_range(period, start_date, end_date)
        if start_dt and end_dt:
            period_data = {}
            for p in products:
                past_in = InventoryTransaction.objects.filter(product=p, transaction_type='IN', created_at__lt=start_dt).aggregate(s=Sum('quantity'))['s'] or 0
                past_out = InventoryTransaction.objects.filter(product=p, transaction_type='OUT', created_at__lt=start_dt).aggregate(s=Sum('quantity'))['s'] or 0
                opening = past_in - past_out
                
                added = InventoryTransaction.objects.filter(product=p, transaction_type='IN', created_at__range=(start_dt, end_dt)).aggregate(s=Sum('quantity'))['s'] or 0
                issued = InventoryTransaction.objects.filter(product=p, transaction_type='OUT', created_at__range=(start_dt, end_dt)).aggregate(s=Sum('quantity'))['s'] or 0
                
                period_data[p.id] = {
                    'opening': opening,
                    'added': added,
                    'issued': issued,
                    'closing': opening + added - issued
                }

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Build a dict: product_id → last ActivityLog with quantity info
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
            "sizes": Size.objects.all()
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
                from inventory.models import InventoryTransaction, Warehouse
                from inventory.services.inventory_service import InventoryService
                
                selected_warehouse = form.cleaned_data.get('warehouse')
                if not selected_warehouse:
                    selected_warehouse = Warehouse.objects.first()
                    
                if selected_warehouse:
                    trans = InventoryTransaction(
                        product=product,
                        transaction_type='IN',
                        quantity=product.quantity,
                        warehouse=selected_warehouse,
                        notes='رصيد افتتاحي (عند إضافة المنتج)'
                    )
                    InventoryService.process(trans)

            messages.success(
            request,
            "تم إضافة المنتج بنجاح."
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
                "تم تعديل المنتج بنجاح."
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
                "لا يمكن حذف منتج له حركات مخزنية. احتفظ به للأرشفة التاريخية.",
            )
        else:
            messages.success(request, "تم حذف المنتج بنجاح.")

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
    
    basic_qty = all_transactions.filter(notes__contains='رصيد افتتاحي').aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    added_qty = all_transactions.filter(transaction_type='IN').exclude(notes__contains='رصيد افتتاحي').aggregate(Sum('quantity'))['quantity__sum'] or 0
    
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
