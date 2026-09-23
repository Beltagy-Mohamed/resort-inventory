import re

path = r'E:\خاص مشروع\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Add to context
old_context = '''            "categories": Category.objects.all(),
            "colors": Color.objects.all(),
            "sizes": Size.objects.all()
        }'''
new_context = '''            "categories": Category.objects.all(),
            "colors": Color.objects.all(),
            "sizes": Size.objects.all(),
            "warehouses": Warehouse.objects.all(),
            "warehouse_id": warehouse_id
        }'''

# Ensure Warehouse is imported
if 'from inventory.models import' in c and 'Warehouse' not in c:
    c = re.sub(r'from inventory\.models import (.*?)\n', r'from inventory.models import \1, Warehouse\n', c, count=1)

c = c.replace(old_context, new_context)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
