import re

path = r'E:\خاص مشروع\client_delivery\inventory\views\settings.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

optimized_view = '''@user_passes_test(superuser_required, login_url='/')
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
                barcode = str(row[0]).strip() if row[0] else None
                name = str(row[1]).strip() if row[1] else (barcode or "بدون اسم")
                cat_name = str(row[2]).strip() if len(row) > 2 and row[2] else None
                
                try:
                    supplied = int(row[3]) if len(row) > 3 and row[3] else 0
                    remaining = int(row[4]) if len(row) > 4 and row[4] else 0
                except (ValueError, TypeError):
                    messages.error(request, f'خطأ في السطر رقم {i + 2} (المنتج: {name}): تأكد من أن الكميات مكتوبة كأرقام.')
                    return redirect('import_stock_excel')
                    
                part_name = str(row[5]).strip() if len(row) > 5 and row[5] else None
                
                if cat_name: category_names.add(cat_name)
                if part_name: partner_names.add(part_name)
                
                product_data.append({
                    'barcode': barcode,
                    'name': name,
                    'category': cat_name,
                    'supplied': supplied,
                    'remaining': remaining,
                    'partner': part_name
                })
            
            from django.db import transaction
            from inventory.models import Stock, Partner
            
            with transaction.atomic():
                # --- 3. Bulk Create Categories & Partners ---
                existing_cats = {c.name: c for c in Category.objects.filter(name__in=category_names)}
                new_cats = [Category(name=c) for c in category_names if c not in existing_cats]
                if new_cats:
                    Category.objects.bulk_create(new_cats)
                    existing_cats.update({c.name: c for c in Category.objects.filter(name__in=category_names)})
                
                existing_parts = {p.name: p for p in Partner.all_objects.filter(name__in=partner_names)}
                new_parts = [Partner(name=p, partner_type='SUPPLIER') for p in partner_names if p not in existing_parts]
                if new_parts:
                    Partner.all_objects.bulk_create(new_parts)
                    existing_parts.update({p.name: p for p in Partner.all_objects.filter(name__in=partner_names)})
                
                # --- 4. Bulk Create Products ---
                all_product_names = [d['name'] for d in product_data]
                all_product_barcodes = [d['barcode'] for d in product_data if d['barcode']]
                
                existing_prods_by_name = {p.name: p for p in Product.all_objects.filter(name__in=all_product_names)}
                existing_prods_by_barcode = {p.barcode: p for p in Product.all_objects.filter(barcode__in=all_product_barcodes)}
                
                new_products = []
                for d in product_data:
                    p = existing_prods_by_barcode.get(d['barcode']) or existing_prods_by_name.get(d['name'])
                    if not p:
                        new_p = Product(
                            name=d['name'],
                            barcode=d['barcode'],
                            category=existing_cats.get(d['category']),
                            quantity=0
                        )
                        new_products.append(new_p)
                        # Add temporarily to prevent duplicates in same file
                        existing_prods_by_name[d['name']] = new_p
                
                if new_products:
                    Product.objects.bulk_create(new_products)
                    # Refresh to get IDs
                    existing_prods_by_name = {p.name: p for p in Product.all_objects.filter(name__in=all_product_names)}
                    existing_prods_by_barcode = {p.barcode: p for p in Product.all_objects.filter(barcode__in=all_product_barcodes)}
                
                # --- 5. Prepare Transactions and Stocks ---
                transactions_to_create = []
                # Fetch existing stock to update memory
                product_ids = [p.id for p in existing_prods_by_name.values()]
                existing_stocks = {s.product_id: s for s in Stock.objects.filter(warehouse=warehouse, product_id__in=product_ids)}
                
                stocks_to_update = []
                stocks_to_create = []
                
                for d in product_data:
                    p = existing_prods_by_barcode.get(d['barcode']) or existing_prods_by_name.get(d['name'])
                    part_obj = existing_parts.get(d['partner'])
                    
                    if d['supplied'] > 0:
                        transactions_to_create.append(InventoryTransaction(
                            product=p, transaction_type='IN', quantity=d['supplied'],
                            warehouse=warehouse, partner=part_obj, notes='استيراد مخزون (ما تم توريده)'
                        ))
                    
                    if d['remaining'] < d['supplied']:
                        transactions_to_create.append(InventoryTransaction(
                            product=p, transaction_type='OUT', quantity=d['supplied'] - d['remaining'],
                            warehouse=warehouse, notes='استيراد مخزون (تسوية المتبقي)'
                        ))
                    elif d['remaining'] > d['supplied']:
                        transactions_to_create.append(InventoryTransaction(
                            product=p, transaction_type='IN', quantity=d['remaining'] - d['supplied'],
                            warehouse=warehouse, notes='استيراد مخزون (تسوية زيادة المتبقي)'
                        ))
                        
                    # Calculate new stock for this warehouse
                    # We just override the stock quantity with "remaining" since it's an initial load
                    stock = existing_stocks.get(p.id)
                    if stock:
                        stock.quantity = d['remaining']
                        stocks_to_update.append(stock)
                    else:
                        new_stock = Stock(product=p, warehouse=warehouse, quantity=d['remaining'])
                        stocks_to_create.append(new_stock)
                        existing_stocks[p.id] = new_stock # Prevents duplicates if same product appears twice
                        
                    # Also update global product quantity
                    p.quantity = d['remaining']
                
                # --- 6. Execute Bulk Operations ---
                if transactions_to_create:
                    InventoryTransaction.objects.bulk_create(transactions_to_create)
                
                if stocks_to_create:
                    Stock.objects.bulk_create(stocks_to_create)
                if stocks_to_update:
                    Stock.objects.bulk_update(stocks_to_update, ['quantity'])
                    
                Product.objects.bulk_update(list(existing_prods_by_name.values()), ['quantity'])

            messages.success(request, f'تم استيراد ومعالجة {len(product_data)} منتج بنجاح وبسرعة فائقة.')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الاستيراد: {str(e)}')
            
        return redirect('import_stock_excel')
        
    # Show all warehouses (including leader-only) for superusers and Leader group
    if request.user.is_superuser or request.user.groups.filter(name__in=['Leader', 'LeaderStaff']).exists():
        warehouses = Warehouse.all_objects.all()
    else:
        warehouses = Warehouse.objects.all()
    return render(request, 'settings/import_excel.html', {'warehouses': warehouses})'''

c = re.sub(r'@user_passes_test\(superuser_required, login_url=\'/\'\)\ndef import_stock_excel\(request\):.*?return render\(request, \'settings/import_excel\.html\', \{\'warehouses\': warehouses\}\)', optimized_view, c, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Optimized import_stock_excel written")
