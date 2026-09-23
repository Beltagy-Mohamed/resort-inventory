path = r'E:\خاص مشروع\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

bad_lines = lines[197:218]

good_lines = [
    '                from inventory.models import InventoryTransaction\n',
    '                trans = InventoryTransaction(\n',
    '                    product=product,\n',
    '                    transaction_type="IN",\n',
    '                    quantity=product.quantity,\n',
    '                    notes="رصيد افتتاحي"\n',
    '                )\n',
]

lines[197:218] = good_lines

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
