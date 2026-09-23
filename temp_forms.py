path = r'E:\خاص مشروع\client_delivery\inventory\forms.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('"minimum_stock", "is_leadership_restricted", "description"', '"target_quantity", "minimum_stock", "is_leadership_restricted", "description"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
