import re

path = r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
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

    products = Product.all_objects.filter(is_leadership_restricted=True).select_related("category", "color", "size")
    
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

    products = products.order_by("-id").distinct()'''

c = re.sub(r'    search = request\.GET\.get\("search", ""\).*?    products = products\.order_by\("-id"\)(\.distinct\(\))?', new_logic, c, flags=re.DOTALL)

from_str = 'return render(request, "leadership/list.html", {'
to_str = 'from inventory.models import Warehouse\n    warehouses = Warehouse.all_objects.all()\n    ' + from_str + '\n        "warehouses": warehouses,\n        "warehouse_id": warehouse_id,'
if 'warehouses = Warehouse.all_objects.all()' not in c:
    c = c.replace(from_str, to_str)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
