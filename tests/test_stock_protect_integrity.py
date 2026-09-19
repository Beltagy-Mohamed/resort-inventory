import pytest
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from inventory.models import Product, Stock, InventoryTransaction

@pytest.mark.django_db
def test_both_fk_relations_are_protected(product_factory, warehouse_factory):
    # Create product and warehouse
    product = product_factory(quantity=10)
    warehouse = warehouse_factory()
    
    # Create Stock explicitly if not created by signals
    stock, _ = Stock.objects.get_or_create(product=product, warehouse=warehouse, defaults={"quantity": 10})
    
    # Create a transaction
    trans = InventoryTransaction.objects.create(
        product=product,
        warehouse=warehouse,
        transaction_type='IN',
        quantity=10,
    )
    
    # Verify transaction exists
    assert InventoryTransaction.objects.count() == 1
    
    # Try deleting the product
    # Since Stock and InventoryTransaction use PROTECT (or should), this should raise ProtectedError
    with pytest.raises((ProtectedError, IntegrityError)) as excinfo:
        product.delete()
        
    # The product shouldn't be deleted
    assert Product.objects.count() == 1
    
    # The error message should mention either InventoryTransaction or Stock
    error_msg = str(excinfo.value)
    assert "inventorytransaction" in error_msg.lower() or "stock" in error_msg.lower()
