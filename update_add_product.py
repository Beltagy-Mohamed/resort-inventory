import os

path = r'g:\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''            # Create initial stock transaction if quantity > 0
            if product.quantity > 0:
                from inventory.models import InventoryTransaction
                InventoryTransaction.objects.create(
                    product=product,
                    transaction_type='IN',
                    quantity=product.quantity,
                    notes='رصيد افتتاحي (عند الإضافة)'
                )'''

repl = '''            # Create initial stock transaction if quantity > 0
            if product.quantity > 0:
                from inventory.models import InventoryTransaction, Warehouse
                from inventory.services.inventory_service import InventoryService
                
                default_warehouse = Warehouse.objects.first()
                if default_warehouse:
                    trans = InventoryTransaction(
                        product=product,
                        transaction_type='IN',
                        quantity=product.quantity,
                        warehouse=default_warehouse,
                        notes='رصيد افتتاحي (عند الإضافة)'
                    )
                    InventoryService.process(trans)'''

c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
