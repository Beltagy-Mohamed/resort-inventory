from django.db import migrations

def populate_default_warehouse(apps, schema_editor):
    Warehouse = apps.get_model('inventory', 'Warehouse')
    Product = apps.get_model('inventory', 'Product')
    Stock = apps.get_model('inventory', 'Stock')
    InventoryTransaction = apps.get_model('inventory', 'InventoryTransaction')

    # Create the default warehouse if it doesn't exist
    if not Warehouse.objects.exists():
        default_warehouse = Warehouse.objects.create(
            name="المخزن الرئيسي",
            location="المركز الرئيسي",
            manager="System Auto-Generated"
        )
    else:
        default_warehouse = Warehouse.objects.first()

    # Move product quantities to Stock
    for product in Product.objects.all():
        if product.quantity > 0:
            Stock.objects.get_or_create(
                product=product,
                warehouse=default_warehouse,
                defaults={'quantity': product.quantity}
            )

    # Assign all previous transactions to the default warehouse
    InventoryTransaction.objects.filter(warehouse__isnull=True).update(warehouse=default_warehouse)

def reverse_populate(apps, schema_editor):
    pass # No safe reverse needed

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_partner_warehouse_remove_product_price_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_default_warehouse, reverse_populate),
    ]
