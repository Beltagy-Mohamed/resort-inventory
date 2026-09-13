from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.urls import reverse

from inventory.models import InventoryTransaction, Product, Warehouse
from inventory.services.inventory_service import InventoryService

class DeploymentReadinessTest(TestCase):
    def test_whitenoise_installed_for_static_files(self):
        self.assertIn(
            'whitenoise.middleware.WhiteNoiseMiddleware', 
            settings.MIDDLEWARE, 
            'Whitenoise is missing from MIDDLEWARE'
        )

    def test_database_url_support(self):
        try:
            import dj_database_url
        except ImportError:
            self.fail('dj_database_url is not installed, which is required for Render/Supabase DATABASE_URL parsing')


class InventorySafetyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("staff", password="safe-password-123")
        self.warehouse = Warehouse.objects.create(name="الرئيسي")
        self.product = Product.objects.create(name="مناشف", cost_price=10, selling_price=15)

    def process(self, transaction_type, quantity):
        return InventoryService.process(InventoryTransaction(
            product=self.product,
            warehouse=self.warehouse,
            transaction_type=transaction_type,
            quantity=quantity,
        ))

    def test_stock_movements_update_warehouse_and_global_balance(self):
        self.process("IN", 10)
        self.process("OUT", 4)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 6)
        self.assertEqual(self.product.stocks.get(warehouse=self.warehouse).quantity, 6)

    def test_out_cannot_exceed_warehouse_balance(self):
        self.process("IN", 2)
        with self.assertRaises(ValidationError):
            self.process("OUT", 3)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 2)

    def test_product_with_transactions_cannot_be_deleted(self):
        self.process("IN", 1)
        with self.assertRaises(ProtectedError):
            self.product.delete()

    def test_reports_require_transaction_view_permission(self):
        self.client.login(username="staff", password="safe-password-123")
        response = self.client.get(reverse("inventory_report"))
        self.assertEqual(response.status_code, 403)
        permission = Permission.objects.get(codename="view_inventorytransaction")
        self.user.user_permissions.add(permission)
        response = self.client.get(reverse("inventory_report"))
        self.assertEqual(response.status_code, 200)
