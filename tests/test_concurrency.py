import threading
import pytest
from django.db import connections
from inventory.models import InventoryTransaction
from inventory.services.inventory_service import InventoryService
from django.core.exceptions import ValidationError

@pytest.mark.concurrency
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("run", range(20)) # Run 20 times as per TEST_PLAN
def test_concurrent_issue_never_goes_negative(product_factory, warehouse_factory, run):
    # This test verifies that even under concurrent pressure, a product's stock cannot become negative
    product = product_factory(quantity=10)
    warehouse = warehouse_factory()
    
    # We must ensure the initial stock is set in the DB
    initial_trans = InventoryTransaction(
        product=product,
        warehouse=warehouse,
        transaction_type='IN',
        quantity=10,
        notes='Initial stock'
    )
    InventoryService.process(initial_trans)
    product.refresh_from_db()
    
    results = []

    def issue_stock(qty):
        # Close connection to force new thread to open its own connection
        connections.close_all()
        try:
            trans = InventoryTransaction(
                product=product,
                warehouse=warehouse,
                transaction_type='OUT',
                quantity=qty
            )
            InventoryService.process(trans)
            results.append("success")
        except ValidationError:
            # We expect a ValidationError when stock goes negative
            results.append("rejected")
        except Exception as e:
            results.append(f"error: {str(e)}")

    # 2 threads trying to issue 8 items each. Total 16 > 10.
    t1 = threading.Thread(target=issue_stock, args=(8,))
    t2 = threading.Thread(target=issue_stock, args=(8,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    product.refresh_from_db()
    
    # The absolute critical assertion: Stock MUST NOT be negative
    assert product.quantity >= 0
    
    # If using proper locking (e.g. select_for_update), exactly one should succeed and one should fail
    # Note: On SQLite, this might falsely pass due to DB-level lock. The plan requires Postgres.
    assert results.count("success") == 1
    assert results.count("rejected") == 1
