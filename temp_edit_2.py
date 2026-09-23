import os

path = r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

imports = 'from django.db.models import Q, F, Sum\nfrom django.db.models.functions import Coalesce\n'
if 'from django.db.models.functions import Coalesce' not in c:
    c = imports + c

old_qs = 'products = Product.all_objects.filter(is_leadership_restricted=True).order_by("-id")'
new_qs = 'products = Product.all_objects.filter(is_leadership_restricted=True).annotate(total_supplied=Coalesce(Sum("inventorytransaction__quantity", filter=Q(inventorytransaction__transaction_type="IN")), 0)).order_by("-id")'

if 'total_supplied=Coalesce' not in c:
    c = c.replace(old_qs, new_qs)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Modified leadership.py")
