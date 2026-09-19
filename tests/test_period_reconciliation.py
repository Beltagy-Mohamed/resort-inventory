import pytest
from inventory.models import InventoryTransaction
from inventory.services.inventory_service import InventoryService

@pytest.mark.django_db
def test_period_reconciliation_math(product_factory, warehouse_factory):
    product = product_factory(quantity=0)
    warehouse = warehouse_factory()
    
    # math: old + added - removed = new
    InventoryService.process(InventoryTransaction(product=product, warehouse=warehouse, transaction_type='IN', quantity=100))
    InventoryService.process(InventoryTransaction(product=product, warehouse=warehouse, transaction_type='OUT', quantity=25))
    
    product.refresh_from_db()
    assert product.quantity == 75
