import re

path = r'E:\خاص مشروع\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

new_logic = '''    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    category_id = request.GET.get("category", "")
    color_id = request.GET.get("color", "")
    size_id = request.GET.get("size", "")
    period = request.GET.get("period", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    warehouse_id = request.GET.get("warehouse", "")

    products = Product.objects.select_related("category", "color", "size")
    
    if warehouse_id:
        products = products.filter(stock__warehouse_id=warehouse_id)
        products = products.annotate(
            total_supplied=Coalesce(Sum("inventorytransaction__quantity", filter=Q(inventorytransaction__transaction_type="IN", inventorytransaction__warehouse_id=warehouse_id)), 0),
            display_quantity=Coalesce(Sum("stock__quantity", filter=Q(stock__warehouse_id=warehouse_id)), 0)
        )
    else:
        products = products.annotate(
            total_supplied=Coalesce(Sum("inventorytransaction__quantity", filter=Q(inventorytransaction__transaction_type="IN")), 0),
            display_quantity=F("quantity")
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
'''

# Find the block from search = to period_data assignment
c = re.sub(r'    search = request\.GET\.get\("search", ""\).*?                period_data\[p\.id\] = \{\n                    \'opening\': opening,\n                    \'added\': added,\n                    \'issued\': issued,\n                    \'closing\': opening \+ added - issued\n                \}\n', new_logic, c, flags=re.DOTALL)

# Add warehouses to render context
from_str = 'return render(request, "products/list.html", {'
to_str = 'from inventory.models import Warehouse\n    warehouses = Warehouse.objects.all()\n    ' + from_str + '\n        "warehouses": warehouses,\n        "warehouse_id": warehouse_id,'

c = c.replace(from_str, to_str)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Updated products_list view logic")
