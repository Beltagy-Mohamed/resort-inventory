import re
path1 = r'E:\خاص مشروع\client_delivery\inventory\views\products.py'
path2 = r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'

for path in [path1, path2]:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # 1. Remove Subquery and latest_supplier annotations
    c = re.sub(r'\s*latest_supplier_sq = InventoryTransaction\.all_objects\.filter\(.*?\)\.order_by\(\'-created_at\'\)\.values\(\'partner__name\'\)\[:1\]', '', c, flags=re.DOTALL)
    
    c = c.replace(",\n            latest_supplier=Subquery(latest_supplier_sq)", "")
    
    # Add select_related('supplier') to the initial query
    # products = Product.objects.all().order_by("-id") -> products = Product.objects.select_related('supplier').all().order_by("-id")
    # For leadership: Product.all_objects.filter(is_leadership_restricted=True).order_by("-id") -> Product.all_objects.select_related('supplier').filter(...)
    if 'products = Product.objects.all()' in c:
        c = c.replace('products = Product.objects.all()', 'products = Product.objects.select_related("supplier").all()')
    if 'products = Product.all_objects.filter(' in c:
        c = c.replace('products = Product.all_objects.filter(', 'products = Product.all_objects.select_related("supplier").filter(')
    
    # 2. Update Excel export
    # getattr(p, 'latest_supplier', "") or "", -> p.supplier.name if p.supplier else "",
    c = c.replace('getattr(p, \'latest_supplier\', "") or "",', 'p.supplier.name if p.supplier else "",')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

# 3. Update HTML templates to use p.supplier.name instead of p.latest_supplier
path_tpl1 = r'E:\خاص مشروع\client_delivery\templates\products\list.html'
path_tpl2 = r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
for path in [path_tpl1, path_tpl2]:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = html.replace('{{ p.latest_supplier|default:"-" }}', '{{ p.supplier.name|default:"-" }}')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
