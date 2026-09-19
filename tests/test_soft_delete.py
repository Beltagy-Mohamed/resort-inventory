import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from inventory.models import InventoryTransaction

User = get_user_model()

@pytest.mark.django_db
def test_delete_user_soft_deletes_instead_of_hard_delete(api_client, superuser, regular_user):
    api_client.force_login(superuser)
    
    user_to_delete = regular_user
    assert user_to_delete.is_active is True
    
    # POST to delete_user view
    url = reverse('delete_user', args=[user_to_delete.pk])
    response = api_client.post(url)
    
    # Check redirect indicating success
    assert response.status_code == 302
    
    # Refresh user
    user_to_delete.refresh_from_db()
    
    # The user should NOT be deleted from DB, only soft-deleted (is_active=False)
    assert user_to_delete.is_active is False
    assert User.objects.filter(pk=user_to_delete.pk).exists()
