import re

path = r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old_context = '''        "quantity_log_map": quantity_log_map,
    }'''
new_context = '''        "quantity_log_map": quantity_log_map,
        "warehouses": Warehouse.objects.all(),
        "warehouse_id": warehouse_id,
    }'''

if 'from inventory.models import' in c and 'Warehouse' not in c:
    c = re.sub(r'from inventory\.models import (.*?)\n', r'from inventory.models import \1, Warehouse\n', c, count=1)

c = c.replace(old_context, new_context)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
