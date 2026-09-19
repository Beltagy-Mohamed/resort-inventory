import pytest
from django.urls import reverse
from inventory.models import InventoryTransaction
from inventory.services.inventory_service import InventoryService

@pytest.mark.django_db
def test_normal_user_cannot_see_leader_transactions(api_client, regular_user, superuser, product_factory, warehouse_factory):
    api_client.force_login(superuser)
    leader_product = product_factory(is_leadership_restricted=True)
    normal_product = product_factory(is_leadership_restricted=False)
    warehouse = warehouse_factory()
    
    # Create transactions
    InventoryService.process(InventoryTransaction(product=leader_product, warehouse=warehouse, transaction_type='IN', quantity=10))
    InventoryService.process(InventoryTransaction(product=normal_product, warehouse=warehouse, transaction_type='IN', quantity=10))
    
    # Login as normal user
    api_client.force_login(regular_user)
    
    # Hit transactions list
    response = api_client.get(reverse('transactions_list'))
    assert response.status_code == 200
    
    # Normal product should be in context
    transactions = response.context['page_obj'].object_list
    assert len(transactions) == 1
    assert transactions[0].product == normal_product
