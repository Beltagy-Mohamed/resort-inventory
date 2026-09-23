import re
path = r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Let's replace the query block in leadership_items_list
old_query = '''    products = Product.all_objects.filter(is_leadership_restricted=True).annotate(total_supplied=Coalesce(Sum("transactions__quantity", filter=Q(transactions__transaction_type="IN")), 0)).order_by("-id")
    search = request.GET.get("search", "")
    if search:
        products = products.filter(name__icontains=search)'''

new_query = '''    products = Product.all_objects.filter(is_leadership_restricted=True).order_by("-id")
    search = request.GET.get("search", "")
    warehouse_id = request.GET.get("warehouse")
    
    from django.db.models import Subquery, OuterRef
    latest_supplier_sq = InventoryTransaction.all_objects.filter(
        product=OuterRef('pk'), transaction_type='IN', partner__isnull=False
    ).order_by('-created_at').values('partner__name')[:1]

    if warehouse_id:
        supplied_expr = Coalesce(Sum('transactions__quantity', filter=Q(transactions__transaction_type='IN', transactions__warehouse_id=warehouse_id)), 0)
        products = products.filter(stocks__warehouse_id=warehouse_id).annotate(
            display_quantity=Coalesce(Sum('stocks__quantity', filter=Q(stocks__warehouse_id=warehouse_id)), 0),
            total_supplied=supplied_expr,
            remaining_target=F('target_quantity') - supplied_expr,
            latest_supplier=Subquery(latest_supplier_sq)
        )
    else:
        supplied_expr = Coalesce(Sum('transactions__quantity', filter=Q(transactions__transaction_type='IN')), 0)
        products = products.annotate(
            display_quantity=F('quantity'),
            total_supplied=supplied_expr,
            remaining_target=F('target_quantity') - supplied_expr,
            latest_supplier=Subquery(latest_supplier_sq)
        )

    if search:
        products = products.filter(name__icontains=search)'''

c = c.replace(old_query, new_query)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
