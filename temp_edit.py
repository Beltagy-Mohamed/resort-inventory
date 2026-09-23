import os

path = r'E:\خاص مشروع\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if 'from django.db.models.functions import Coalesce' not in c:
    c = c.replace('from django.db.models import Q, F, Sum', 'from django.db.models import Q, F, Sum\nfrom django.db.models.functions import Coalesce')

old_qs = 'products = Product.objects.select_related("category", "color", "size")'
new_qs = 'products = Product.objects.select_related("category", "color", "size").annotate(total_supplied=Coalesce(Sum("inventorytransaction__quantity", filter=Q(inventorytransaction__transaction_type="IN")), 0))'

if 'total_supplied=Coalesce' not in c:
    c = c.replace(old_qs, new_qs)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Modified products.py")
