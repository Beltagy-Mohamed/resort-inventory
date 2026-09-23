import re

path = r'E:\خاص مشروع\client_delivery\inventory\views\settings.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

bad = '''                    if not p:
                        new_p = Product(
                            name=d['name'],
                            barcode=d['barcode'],
                            target_quantity=d['target_quantity'],
                            quantity=0
                        )
                    else:
                        p.target_quantity = d['target_quantity']
                        new_products.append(new_p)
                        # Add temporarily to prevent duplicates in same file
                        existing_prods_by_name[d['name']] = new_p'''

good = '''                    if not p:
                        new_p = Product(
                            name=d['name'],
                            barcode=d['barcode'],
                            target_quantity=d['target_quantity'],
                            quantity=0
                        )
                        new_products.append(new_p)
                        # Add temporarily to prevent duplicates in same file
                        existing_prods_by_name[d['name']] = new_p
                    else:
                        p.target_quantity = d['target_quantity']
                        # We don't overwrite barcode here based on user request "الكود مربوط بالمنتج ميتغيرش نهائيا"'''

c = c.replace(bad, good)
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
