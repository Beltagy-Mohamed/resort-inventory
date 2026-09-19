import pytest
from inventory.models import InventoryTransaction, ActivityLog
from inventory.services.inventory_service import InventoryService

@pytest.mark.django_db
def test_activity_log_records_old_and_new_quantities(product_factory, warehouse_factory):
    product = product_factory(quantity=0)
    warehouse = warehouse_factory()
    
    # 1. Add IN transaction of 10
    trans_in = InventoryTransaction(
        product=product,
        warehouse=warehouse,
        transaction_type='IN',
        quantity=10,
        notes='IN_TRANS'
    )
    InventoryService.process(trans_in)
    
    # Check activity log for this trans
    log_in = ActivityLog.objects.filter(product=product, action='IN').first()
    assert log_in is not None
    assert log_in.old_quantity == 0
    assert log_in.new_quantity == 10
    
    # 2. Add OUT transaction of 3
    trans_out = InventoryTransaction(
        product=product,
        warehouse=warehouse,
        transaction_type='OUT',
        quantity=3,
        notes='OUT_TRANS'
    )
    InventoryService.process(trans_out)
    
    # Check activity log for this trans
    log_out = ActivityLog.objects.filter(product=product, action='OUT').first()
    assert log_out is not None
    assert log_out.old_quantity == 10
    assert log_out.new_quantity == 7
