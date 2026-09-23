import re
paths = [
    r'E:\خاص مشروع\client_delivery\inventory\views\products.py',
    r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    replacement = '''
    from inventory.models import InventoryTransaction
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
'''

    pattern = re.compile(r'    from inventory\.models import InventoryTransaction.*?        \)', re.DOTALL)
    c = pattern.sub(replacement.strip('\n'), c)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
