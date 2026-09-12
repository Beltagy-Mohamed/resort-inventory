import os

path = r'g:\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if "reference='رصيد افتتاحي (عند الإضافة)'" in c:
    c = c.replace(
        "reference='رصيد افتتاحي (عند الإضافة)'",
        "notes='رصيد افتتاحي (عند الإضافة)'"
    )
elif 'reference="رصيد افتتاحي (عند الإضافة)"' in c:
    c = c.replace(
        'reference="رصيد افتتاحي (عند الإضافة)"',
        'notes="رصيد افتتاحي (عند الإضافة)"'
    )
else:
    # Just generic replace
    c = c.replace("reference=", "notes=")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
