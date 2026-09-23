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
                    
                if not row[1] and not row[0]: # Require either barcode or name
                    continue
                    
                barcode = str(row[0]).strip() if row[0] else None
                name = str(row[1]).strip() if row[1] else (barcode or "بدون اسم")
                category_name = str(row[2]).strip() if len(row) > 2 and row[2] else None
                

                try:
                    supplied = int(row[3]) if len(row) > 3 and row[3] else 0
                    remaining = int(row[4]) if len(row) > 4 and row[4] else 0
                except (ValueError, TypeError):
                    messages.error(request, f'خطأ في السطر رقم {rows_processed + 2} (المنتج: {name}): تأكد من أن الكميات مكتوبة كأرقام فقط.')
                    return redirect('import_stock_excel')
                
                partner_name = str(row[5]).strip() if len(row) > 5 and row[5] else None
                partner_obj = None
                if partner_name:
                    from inventory.models import Partner
                    partner_obj, _ = Partner.all_objects.get_or_create(name=partner_name, defaults={'partner_type': 'SUPPLIER'})

                
                cat_obj = None
                if category_name:
                    cat_obj, _ = Category.objects.get_or_create(name=category_name)
                
                # Try to find by barcode if provided, else by name
                product = None
                if barcode:
                    product = Product.all_objects.filter(barcode=barcode).first()
                if not product:
                    product = Product.all_objects.filter(name=name).first()
                    
                if not product:
                    product = Product.objects.create(
                        name=name,
                        category=cat_obj,
                        barcode=barcode,
                        quantity=0
                    )
                else:
                    if not product.barcode and barcode:
                        product.barcode = barcode
                    if not product.category and cat_obj:
                        product.category = cat_obj
                    product.save()
                
                if supplied > 0:
                    trans_in = InventoryTransaction(
                        product=product,
                        transaction_type='IN',
                        quantity=supplied,
                        warehouse=warehouse,
                        partner=partner_obj,
                        notes='استيراد مخزون (ما تم توريده)'
                    )
                    InventoryService.process(trans_in)
                
                if remaining < supplied:
                    out_qty = supplied - remaining
                    trans_out = InventoryTransaction(
                        product=product,
                        transaction_type='OUT',
                        quantity=out_qty,
                        warehouse=warehouse,
                        notes='استيراد مخزون (تسوية المتبقي)'
                    )
                    InventoryService.process(trans_out)
                elif remaining > supplied:
                    adj_qty = remaining - supplied
                    trans_adj = InventoryTransaction(
                        product=product,
                        transaction_type='IN',
                        quantity=adj_qty,
                        warehouse=warehouse,
                        notes='استيراد مخزون (تسوية زيادة المتبقي)'
                    )
                    InventoryService.process(trans_adj)
                
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
