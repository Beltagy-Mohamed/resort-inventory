import pytest
from django.urls import reverse
from inventory.models import Product, Warehouse, Category, Partner

@pytest.mark.django_db
class TestRBACIsolation:
    @pytest.fixture(autouse=True)
    def setup_data(self, product_factory, warehouse_factory, category_factory, partner_factory):
        # Normal data
        self.public_product = product_factory(name="Public Product", is_leadership_restricted=False)
        self.public_warehouse = warehouse_factory(name="Public WH", is_leader_only=False)
        self.public_category = category_factory(name="Public Cat", is_leader_only=False)
        self.public_partner = partner_factory(name="Public Partner", is_leader_only=False)
        
        # Leader data
        self.leader_product = product_factory(name="Leader Product", is_leadership_restricted=True)
        self.leader_warehouse = warehouse_factory(name="Leader WH", is_leader_only=True)
        self.leader_category = category_factory(name="Leader Cat", is_leader_only=True)
        self.leader_partner = partner_factory(name="Leader Partner", is_leader_only=True)

    def test_regular_user_cannot_access_leader_dashboard(self, api_client, regular_user):
        api_client.force_login(regular_user)
        url = reverse('leadership_dashboard')
        response = api_client.get(url)
        assert response.status_code in [403, 404]

    def test_regular_user_cannot_see_leader_product_in_search(self, api_client, regular_user):
        api_client.force_login(regular_user)
        url = reverse('products_list')
        response = api_client.get(url, {'search': 'Leader Product'})
        assert response.status_code == 200
        # Check context instead of HTML since search term reflects in input value
        page_obj = response.context['page_obj']
        products_in_page = [p.name for p in page_obj.object_list]
        assert 'Leader Product' not in products_in_page
        
    def test_leader_user_can_see_leader_product_in_search(self, api_client, leader_user):
        api_client.force_login(leader_user)
        # Assuming leadership products are listed via /leadership-items/
        url = reverse('leadership_items_list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert 'Leader Product' in response.content.decode('utf-8')

    def test_regular_user_cannot_see_leader_warehouse_in_list(self, api_client, regular_user):
        api_client.force_login(regular_user)
        url = reverse('warehouses_list')
        response = api_client.get(url)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'Public WH' in content
        assert 'Leader WH' not in content
        
    def test_regular_user_cannot_see_leader_partner_in_list(self, api_client, regular_user):
        api_client.force_login(regular_user)
        url = reverse('partners_list')
        response = api_client.get(url)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'Public Partner' in content
        assert 'Leader Partner' not in content
        
    def test_regular_user_cannot_edit_leader_product(self, api_client, regular_user):
        api_client.force_login(regular_user)
        # Even if they guess the ID, they shouldn't see it (should be 404)
        url = reverse('edit_product', args=[self.leader_product.id])
        response = api_client.get(url)
        assert response.status_code == 404
