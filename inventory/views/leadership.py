import csv
import logging
from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from inventory.decorators import leadership_required
from inventory.forms import ProductForm
from inventory.models import LeadershipAccessLog, Product
from inventory.utils import get_client_ip

# Logger for sensitive section
logger = logging.getLogger("inventory.leadership")

def log_leadership_access(request, action, product=None):
    """تسجيل العملية الخاصة بالقائد"""
    LeadershipAccessLog.objects.create(
        user=request.user,
        action=action,
        product=product,
        ip_address=get_client_ip(request)
    )

@leadership_required
def leadership_items_list(request):
    """عرض قائمة أصناف القائد فقط"""
    log_leadership_access(request, "VIEW_LIST")
    
    # استخدام all_objects لجلب المنتجات المقيدة فقط
    products = Product.all_objects.filter(is_leadership_restricted=True).order_by("-id")
    
    # البحث
    search = request.GET.get("search", "")
    if search:
        products = products.filter(name__icontains=search)

    # التصفح (Pagination)
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "leadership/list.html",
        {
            "page_obj": page_obj,
            "search": search,
        }
    )

@leadership_required
def leadership_item_detail(request, pk):
    """عرض تفاصيل صنف قائد"""
    product = get_object_or_404(Product.all_objects.all(), pk=pk, is_leadership_restricted=True)
    log_leadership_access(request, "VIEW_DETAIL", product)
    
    return render(
        request,
        "leadership/detail.html",
        {"product": product}
    )

@leadership_required
def leadership_item_add(request):
    """إضافة صنف جديد مباشرة كصنف قائد مقيد"""
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.is_leadership_restricted = True
            product.save()
            
            # Create initial stock transaction if quantity > 0
            if product.quantity > 0:
                from inventory.models import InventoryTransaction, Warehouse
                from inventory.services.inventory_service import InventoryService
                selected_warehouse = form.cleaned_data.get('initial_warehouse')
                if not selected_warehouse:
                    selected_warehouse = Warehouse.objects.first()
                if selected_warehouse:
                    trans = InventoryTransaction(
                        product=product,
                        transaction_type='IN',
                        quantity=product.quantity,
                        warehouse=selected_warehouse,
                        notes='رصيد افتتاحي (عند إضافة صنف مقيد)'
                    )
                    InventoryService.process(trans)
                    
            log_leadership_access(request, "CREATE", product)
            messages.success(request, "تمت إضافة صنف القائد بنجاح.")
            return redirect("leadership_items_list")
    else:
        form = ProductForm()
        
    return render(request, "leadership/form.html", {"form": form, "action_title": "إضافة صنف قائد"})

@leadership_required
def leadership_item_edit(request, pk):
    """تعديل صنف قائد"""
    product = get_object_or_404(Product.all_objects.all(), pk=pk, is_leadership_restricted=True)
    
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            log_leadership_access(request, "UPDATE", product)
            messages.success(request, "تم تحديث صنف القائد بنجاح.")
            return redirect("leadership_items_list")
    else:
        form = ProductForm(instance=product)
        
    return render(request, "leadership/form.html", {"form": form, "action_title": "تعديل صنف قائد"})

@leadership_required
def leadership_items_export(request):
    """تصدير قائمة أصناف القائد"""
    import openpyxl
    
    log_leadership_access(request, "EXPORT")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "أصناف القائد"
    
    headers = [
        "الرقم", "اسم المنتج", "الفئة", "اللون", "المقاس",
        "سعر التكلفة", "سعر البيع", "الكمية", "الحد الأدنى"
    ]
    ws.append(headers)
    
    products = Product.all_objects.filter(is_leadership_restricted=True).order_by("-id")
    for p in products:
        ws.append([
            p.id,
            p.name,
            p.category.name if p.category else "",
            p.color.name if p.color else "",
            p.size.name if p.size else "",
            float(p.cost_price),
            float(p.selling_price),
            p.quantity,
            p.minimum_stock
        ])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="أصناف_القائد.xlsx"'
    wb.save(response)
    
    return response

