import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_superuser_cannot_delete_self(api_client, superuser):
    api_client.force_login(superuser)
    
    # Try deleting self
    url = reverse('delete_user', args=[superuser.pk])
    response = api_client.post(url)
    
    # Should be redirected to users list with error message
    assert response.status_code == 302
    
    superuser.refresh_from_db()
    assert superuser.is_active is True
