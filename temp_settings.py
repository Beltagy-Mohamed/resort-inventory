import re
path = r'E:\خاص مشروع\client_delivery\inventory\views\settings.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Add saving supplier to Product
old_block = '''                    if d['supplied'] > 0:
                        transactions_to_create.append(InventoryTransaction('''
new_block = '''                    if part_obj:
                        p.supplier = part_obj
                        p.save(update_fields=['supplier'])

                    if d['supplied'] > 0:
                        transactions_to_create.append(InventoryTransaction('''

c = c.replace(old_block, new_block)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
