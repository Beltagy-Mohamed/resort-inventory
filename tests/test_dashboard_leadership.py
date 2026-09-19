import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_dashboard_leadership_numbers(api_client, superuser):
    api_client.force_login(superuser)
    response = api_client.get(reverse('leadership_dashboard'))
    assert response.status_code == 200
