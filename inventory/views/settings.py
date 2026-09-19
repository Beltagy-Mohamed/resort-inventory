from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.shortcuts import redirect, render

from ..forms import SystemSettingsForm
from ..models import SystemSettings


@user_passes_test(lambda u: u.is_superuser)
def system_settings(request):

    settings_obj = SystemSettings.load()

    if request.method == "POST":

        form = SystemSettingsForm(
            request.POST,
            instance=settings_obj
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم حفظ الإعدادات بنجاح."
            )

            return redirect("system_settings")

    else:

        form = SystemSettingsForm(instance=settings_obj)

    return render(
        request,
        "settings/edit.html",
        {
            "form": form
        }
    )

import openpyxl
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from inventory.models import Product, Warehouse, InventoryTransaction, Category
from inventory.services.inventory_service import InventoryService

def superuser_required(user):
    return user.is_superuser

@user_passes_test(superuser_required, login_url='/')
def import_stock_excel(request):
    """(B11) Excel import view for Superuser."""
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, 'برجاء رفع ملف إكسيل.')
            return redirect('import_stock_excel')
            
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'الامتداد المدعوم هو .xlsx فقط.')
            return redirect('import_stock_excel')
            
        warehouse_id = request.POST.get('warehouse')
        if not warehouse_id:
            messages.error(request, 'برجاء اختيار المستودع.')
            return redirect('import_stock_excel')
            
        warehouse = Warehouse.all_objects.filter(id=warehouse_id).first()
        if not warehouse:
            messages.error(request, 'المستودع غير موجود.')
            return redirect('import_stock_excel')
            
        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = wb.active
            
            rows_processed = 0
            for row in sheet.iter_rows(min_row=2, values_only=True): # Skip header
                if rows_processed >= 2000:
                    messages.warning(request, 'تم إيقاف الاستيراد بعد 2000 صف لتجنب الضغط.')
                    break
                    
                if not row[0]: # Assuming column A is product name
                    continue
                    
                name = str(row[0]).strip()
                try:
                    quantity = int(row[1]) if row[1] else 0
                    cost = float(row[2]) if row[2] else 0.0
                    price = float(row[3]) if row[3] else 0.0
                except (ValueError, TypeError):
                    messages.error(request, f'خطأ في السطر رقم {rows_processed + 2} (المنتج: {name}): تأكد من أن الكمية والأسعار مكتوبة كأرقام فقط وليس نصوص (مثل "{row[1]}").')
                    return redirect('import_stock_excel')
                
                category_name = str(row[4]).strip() if len(row) > 4 and row[4] else None
                barcode = str(row[5]).strip() if len(row) > 5 and row[5] else None
                
                cat_obj = None
                if category_name:
                    cat_obj, _ = Category.objects.get_or_create(name=category_name)
                
                product, created = Product.all_objects.get_or_create(
                    name=name,
                    defaults={
                        'category': cat_obj,
                        'cost_price': cost,
                        'selling_price': price,
                        'barcode': barcode,
                        'quantity': 0 # Will add via transaction
                    }
                )
                
                if quantity > 0:
                    trans = InventoryTransaction(
                        product=product,
                        transaction_type='IN',
                        quantity=quantity,
                        warehouse=warehouse,
                        notes='استيراد مخزون (أرصدة أولية)'
                    )
                    InventoryService.process(trans)
                
                rows_processed += 1
                
            messages.success(request, f'تم استيراد {rows_processed} منتج بنجاح.')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الاستيراد: {str(e)}')
            
        return redirect('import_stock_excel')
        
    # Show all warehouses (including leader-only) for superusers and Leader group
    if request.user.is_superuser or request.user.groups.filter(name__in=['Leader', 'LeaderStaff']).exists():
        warehouses = Warehouse.all_objects.all()
    else:
        warehouses = Warehouse.objects.all()
    return render(request, 'settings/import_excel.html', {'warehouses': warehouses})
