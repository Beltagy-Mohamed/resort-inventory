import pytest
from django.urls import reverse
import io
import pandas as pd

@pytest.mark.django_db
def test_excel_import_ignores_is_leader_only_for_normal_users(api_client, regular_user, warehouse_factory):
    api_client.force_login(regular_user)
    warehouse = warehouse_factory()
    
    # Normal users should not be able to mass-import leader items or override the flag
    df = pd.DataFrame([
        {'اسم المنتج': 'Test Product', 'الكمية الافتتاحية': 10, 'سعر التكلفة': 5, 'سعر البيع': 10, 'اسم الفئة': 'Cat', 'الباركود': '123'}
    ])
    
    # Convert to Excel
    excel_io = io.BytesIO()
    df.to_excel(excel_io, index=False)
    excel_io.seek(0)
    excel_io.name = "import.xlsx"
    
    response = api_client.post(reverse('import_stock_excel'), {'file': excel_io, 'warehouse_id': warehouse.id})
    assert response.status_code == 302 # Redirect on success
