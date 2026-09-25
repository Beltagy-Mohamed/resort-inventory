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
    """(B11) Excel import view for Superuser - Auto-detects columns from header."""
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

            # --- 1. Auto-detect columns from header row ---
            header_row = [str(c.value).strip() if c.value else '' for c in sheet[1]]
            col_map = {}
            KNOWN_HEADERS = {
                'الكود': 'barcode', 'كود': 'barcode',
                'اسم الصنف': 'name', 'الاسم': 'name', 'اسم المنتج': 'name',
                'التنميط': 'target', 'تنميط': 'target',
                'ما تم توريده': 'supplied', 'الوارد': 'supplied', 'تم توريده': 'supplied',
                'المتبقي': 'remaining', 'متبقي': 'remaining',
                'اسم الشركة': 'company', 'الشركة': 'company', 'المورد': 'company',
            }
            for idx, h in enumerate(header_row):
                for ar_name, key in KNOWN_HEADERS.items():
                    if ar_name in h:
                        col_map[key] = idx
                        break

            # Fallback defaults if header detection fails
            ci_barcode = col_map.get('barcode', 0)
            ci_name = col_map.get('name', 1)
            ci_target = col_map.get('target', 2)
            ci_supplied = col_map.get('supplied', 3)
            ci_remaining = col_map.get('remaining', 4)
            ci_company = col_map.get('company', 5)

            # --- 2. Read all rows into memory ---
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if len(rows) >= 2000:
                    messages.warning(request, 'تم الاكتفاء بـ 2000 صف لتجنب الضغط.')
                    break
                # Skip completely empty rows
                name_val = row[ci_name] if len(row) > ci_name else None
                code_val = row[ci_barcode] if len(row) > ci_barcode else None
                if not name_val and not code_val:
                    continue
                rows.append(row)

            if not rows:
                messages.warning(request, 'الملف فارغ أو لا يحتوي على بيانات صحيحة.')
                return redirect('import_stock_excel')

            # --- 3. Parse product data ---
            partner_names = set()
            product_data = []

            for i, row in enumerate(rows):
                val = row[ci_barcode] if len(row) > ci_barcode else None
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                barcode = str(val).strip() if val is not None else None
                name = str(row[ci_name]).strip() if (len(row) > ci_name and row[ci_name]) else (barcode or "بدون اسم")
                try:
                    target_qty = int(row[ci_target]) if len(row) > ci_target and row[ci_target] else 0
                    supplied = int(row[ci_supplied]) if len(row) > ci_supplied and row[ci_supplied] else 0
                except (ValueError, TypeError):
                    messages.error(request, f'خطأ في السطر رقم {i + 2} (المنتج: {name}): تأكد من أن الكميات مكتوبة كأرقام.')
                    return redirect('import_stock_excel')

                part_name = str(row[ci_company]).strip() if len(row) > ci_company and row[ci_company] else None
                if part_name:
                    partner_names.add(part_name)

                product_data.append({
                    'barcode': barcode,
                    'name': name,
                    'target_quantity': target_qty,
                    'supplied': supplied,
                    'partner': part_name,
                })

            from django.db import transaction
            from inventory.models import Stock, Partner

            with transaction.atomic():
                # --- 4. Bulk Create Partners ---
                existing_parts = {p.name: p for p in Partner.all_objects.filter(name__in=partner_names)}
                new_parts = [Partner(name=p, partner_type='SUPPLIER') for p in partner_names if p not in existing_parts]
                if new_parts:
                    Partner.all_objects.bulk_create(new_parts)
                    existing_parts.update({p.name: p for p in Partner.all_objects.filter(name__in=partner_names)})

                # --- 5. Create / match Products by (name + company) ---
                all_product_names = [d['name'] for d in product_data]
                existing_prods_list = Product.all_objects.select_related('supplier').filter(name__in=all_product_names)
                existing_prods_by_key = {(p.name, p.supplier.name if p.supplier else None): p for p in existing_prods_list}

                new_products = []
                for d in product_data:
                    key = (d['name'], d['partner'])
                    p = existing_prods_by_key.get(key)
                    if not p:
                        new_p = Product(
                            name=d['name'],
                            barcode=d['barcode'],
                            target_quantity=d['target_quantity'],
                            quantity=0,
                            supplier=existing_parts.get(d['partner']),
                        )
                        new_products.append(new_p)
                        existing_prods_by_key[key] = new_p
                    else:
                        p.target_quantity = d['target_quantity']

                if new_products:
                    Product.all_objects.bulk_create(new_products)
                    existing_prods_list = Product.all_objects.select_related('supplier').filter(name__in=all_product_names)
                    existing_prods_by_key = {(p.name, p.supplier.name if p.supplier else None): p for p in existing_prods_list}

                # --- 6. Prepare Transactions and Stocks ---
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
                            warehouse=warehouse, partner=part_obj, notes='وارد أولي (من ملف الإكسيل)',
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

                # --- 7. Execute Bulk Operations ---
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

