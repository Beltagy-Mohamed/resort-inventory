import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_reports_reject_invalid_warehouse_id_not_digit(api_client, superuser):
    # Regression test for A7
    api_client.force_login(superuser)
    url = reverse('warehouse_stock_report')
    response = api_client.get(url, {'warehouse_id': 'DROP TABLE'})
    # View should either return 400 or render empty/ignore but NOT throw a ValueError
    assert response.status_code in [200, 400]
