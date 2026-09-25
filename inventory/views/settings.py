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
    """(B11) Excel import view for Superuser - Highly Optimized for Vercel 10s Timeout."""
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
            
            # --- 1. Read all rows into memory ---
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if len(rows) >= 2000:
                    messages.warning(request, 'تم الاكتفاء بـ 2000 صف لتجنب الضغط.')
                    break
                if not row[1] and not row[0]:
                    continue
                rows.append(row)
            
            if not rows:
                messages.warning(request, 'الملف فارغ أو لا يحتوي على بيانات صحيحة.')
                return redirect('import_stock_excel')
            
            # --- 2. Extract unique names for bulk operations ---
            category_names = set()
            partner_names = set()
            product_data = []
            
            for i, row in enumerate(rows):
                val = row[0]
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                barcode = str(val).strip() if val is not None else None
                name = str(row[1]).strip() if row[1] else (barcode or "بدون اسم")
                try:
                    target_qty = int(row[2]) if len(row) > 2 and row[2] else 0
                    supplied = int(row[3]) if len(row) > 3 and row[3] else 0
                    remaining = int(row[4]) if len(row) > 4 and row[4] else 0
                except (ValueError, TypeError):
                    messages.error(request, f'خطأ في السطر رقم {i + 2} (المنتج: {name}): تأكد من أن الكميات مكتوبة كأرقام.')
                    return redirect('import_stock_excel')
                    
                part_name = str(row[7]).strip() if len(row) > 7 and row[7] else None
                
                if part_name: partner_names.add(part_name)
                
                product_data.append({
                    'barcode': barcode,
                    'name': name,
                    'target_quantity': target_qty,
                    'supplied': supplied,
                    'remaining': remaining,
                    'partner': part_name
                })
            
            from django.db import transaction
            from inventory.models import Stock, Partner
            
            with transaction.atomic():
                # --- 3. Bulk Create Partners ---
                existing_parts = {p.name: p for p in Partner.all_objects.filter(name__in=partner_names)}
                new_parts = [Partner(name=p, partner_type='SUPPLIER') for p in partner_names if p not in existing_parts]
                if new_parts:
                    Partner.all_objects.bulk_create(new_parts)
                    existing_parts.update({p.name: p for p in Partner.all_objects.filter(name__in=partner_names)})
                
                                  # --- 4. Bulk Create Products ---
                  all_product_names = [d['name'] for d in product_data]
                  
                  existing_prods_list = Product.all_objects.select_related('supplier').filter(name__in=all_product_names)
                  existing_prods_by_key = {(p.name, p.supplier.name if p.supplier else None): p for p in existing_prods_list}
                  
                  new_products = []
                  for d in product_data:
                      part_name = d['partner']
                      key = (d['name'], part_name)
                      p = existing_prods_by_key.get(key)
                      
                      if not p:
                          new_p = Product(
                              name=d['name'],
                              barcode=d['barcode'],
                              target_quantity=d['target_quantity'],
                              quantity=0,
                              supplier=existing_parts.get(part_name)
                          )
                          new_products.append(new_p)
                          existing_prods_by_key[key] = new_p
                      else:
                          p.target_quantity = d['target_quantity']
                  
                  if new_products:
                      Product.objects.bulk_create(new_products)
                      # Refresh to get IDs
                      existing_prods_list = Product.all_objects.select_related('supplier').filter(name__in=all_product_names)
                      existing_prods_by_key = {(p.name, p.supplier.name if p.supplier else None): p for p in existing_prods_list}
                  
                  # --- 5. Prepare Transactions and Stocks ---
                  transactions_to_create = []
                  product_ids = [p.id for p in existing_prods_by_key.values() if p.id]
                  existing_stocks = {s.product_id: s for s in Stock.all_objects.filter(warehouse=warehouse, product_id__in=product_ids)}
                  
                  stocks_to_update = []
                  stocks_to_create = []
                  
                  for d in product_data:
                      key = (d['name'], d['partner'])
                      p = existing_prods_by_key.get(key)
                      part_obj = existing_parts.get(d['partner'])
                      
                      if d['supplied'] > 0:
                          transactions_to_create.append(InventoryTransaction(
                              product=p, transaction_type='IN', quantity=d['supplied'],
                              warehouse=warehouse, partner=part_obj, notes='وارد أولي (من ملف الإكسيل)'
                          ))
                      
                      stock = existing_stocks.get(p.id)
                      if stock:
                          stock.quantity += d['supplied']
                          if stock not in stocks_to_update:
                              stocks_to_update.append(stock)
                      else:
                          new_stock = Stock(product=p, warehouse=warehouse, quantity=d['supplied'])
                          stocks_to_create.append(new_stock)
                          existing_stocks[p.id] = new_stock
                      
                      p.quantity = (p.quantity or 0) + d['supplied']
                  
                  # --- 6. Execute Bulk Operations ---
                if transactions_to_create:
                    InventoryTransaction.all_objects.bulk_create(transactions_to_create)
                
                if stocks_to_create:
                    Stock.all_objects.bulk_create(stocks_to_create)
                if stocks_to_update:
                    Stock.all_objects.bulk_update(stocks_to_update, ['quantity'])
                    
                Product.all_objects.bulk_update(list(existing_prods_by_key.values()), ['quantity'])

            messages.success(request, f'تم استيراد ومعالجة {len(product_data)} منتج بنجاح وبسرعة فائقة.')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الاستيراد: {str(e)}')
            
        return redirect('import_stock_excel')
        
    # Show all warehouses (including leader-only) for superusers and Leader group
    if request.user.is_superuser or request.user.groups.filter(name__in=['Leader', 'LeaderStaff']).exists():
        warehouses = Warehouse.all_objects.all()
    else:
        warehouses = Warehouse.objects.all()
    return render(request, 'settings/import_excel.html', {'warehouses': warehouses})

def wipe_all_data_secret(request):
    from django.http import HttpResponse
    from inventory.models import Product, InventoryTransaction, ActivityLog, Partner, Category, Color, Size
    
    InventoryTransaction.objects.all().delete()
    ActivityLog.objects.all().delete()
    Product.all_objects.all().delete()
    Partner.objects.all().delete()
    Category.objects.all().delete()
    Color.objects.all().delete()
    Size.objects.all().delete()
    
    return HttpResponse("All Products, Categories, Colors, Sizes, Transactions, Activity Logs, and Partners have been completely deleted from the database. You can now re-upload your Excel file.")

