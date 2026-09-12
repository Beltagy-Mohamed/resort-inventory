import os

path = r'g:\client_delivery\inventory\views\users.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'from inventory.models import Product, InventoryTransaction',
    'from inventory.models import Product, InventoryTransaction, Category, Color, Size'
)

repl = '''
    # We assign standard django permissions based on checkboxes
    prod_ct = ContentType.objects.get_for_model(Product)
    trans_ct = ContentType.objects.get_for_model(InventoryTransaction)
    cat_ct = ContentType.objects.get_for_model(Category)
    col_ct = ContentType.objects.get_for_model(Color)
    size_ct = ContentType.objects.get_for_model(Size)
    
    if cleaned_data.get('perm_inventory'):
        user.user_permissions.add(
            Permission.objects.get(content_type=prod_ct, codename='add_product'),
            Permission.objects.get(content_type=prod_ct, codename='change_product'),
            Permission.objects.get(content_type=prod_ct, codename='view_product'),
            Permission.objects.get(content_type=cat_ct, codename='add_category'),
            Permission.objects.get(content_type=cat_ct, codename='change_category'),
            Permission.objects.get(content_type=cat_ct, codename='view_category'),
            Permission.objects.get(content_type=col_ct, codename='add_color'),
            Permission.objects.get(content_type=col_ct, codename='change_color'),
            Permission.objects.get(content_type=col_ct, codename='view_color'),
            Permission.objects.get(content_type=size_ct, codename='add_size'),
            Permission.objects.get(content_type=size_ct, codename='change_size'),
            Permission.objects.get(content_type=size_ct, codename='view_size')
        )
    if cleaned_data.get('perm_sales'):
        user.user_permissions.add(
            Permission.objects.get(content_type=trans_ct, codename='add_inventorytransaction'),
            Permission.objects.get(content_type=trans_ct, codename='change_inventorytransaction'),
            Permission.objects.get(content_type=trans_ct, codename='view_inventorytransaction')
        )
    if cleaned_data.get('perm_delete'):
        user.user_permissions.add(
            Permission.objects.get(content_type=prod_ct, codename='delete_product'),
            Permission.objects.get(content_type=trans_ct, codename='delete_inventorytransaction'),
            Permission.objects.get(content_type=cat_ct, codename='delete_category'),
            Permission.objects.get(content_type=col_ct, codename='delete_color'),
            Permission.objects.get(content_type=size_ct, codename='delete_size')
        )
'''

# Use string slicing or re
import re
c = re.sub(
    r'# We assign standard django permissions based on checkboxes.*?if cleaned_data\.get\(\'perm_delete\'\):.*?Permission\.objects\.get\(content_type=trans_ct, codename=\'delete_inventorytransaction\'\)\n        \)',
    repl.strip(),
    c,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
