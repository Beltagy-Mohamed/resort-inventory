from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.urls import reverse

from inventory.models import (
    ActivityLog,
    InventoryTransaction,
    LeadershipAccessConfig,
    Product,
    Warehouse,
)
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


class LeadershipIsolationTests(TestCase):
    def setUp(self):
        self.leader = User.objects.create_user("leader", password="leader-password-123")
        self.staff = User.objects.create_user("staff", password="staff-password-123")
        self.auditor = User.objects.create_superuser("auditor", "audit@example.test", "audit-password-123")
        self.warehouse = Warehouse.objects.create(name="مخزن القائد")
        self.restricted = Product.all_objects.create(
            name="صنف قائد سري",
            is_leadership_restricted=True,
            cost_price=100,
            selling_price=150,
        )
        InventoryService.process(InventoryTransaction(
            product=self.restricted,
            warehouse=self.warehouse,
            transaction_type="IN",
            quantity=5,
        ))
        LeadershipAccessConfig.objects.create(
            holder=self.leader,
            granted_by_note="اختبار العزل",
        )
        self.staff.user_permissions.add(
            Permission.objects.get(codename="view_product"),
            Permission.objects.get(codename="view_inventorytransaction"),
        )

    def test_general_managers_exclude_restricted_product_data(self):
        self.assertFalse(Product.objects.filter(pk=self.restricted.pk).exists())
        self.assertFalse(InventoryTransaction.objects.filter(product=self.restricted).exists())
        self.assertFalse(self.restricted.stocks.model.objects.filter(product=self.restricted).exists())
        self.assertFalse(ActivityLog.objects.filter(product=self.restricted).exists())

    def test_staff_cannot_see_restricted_data_or_leadership_routes(self):
        self.client.login(username="staff", password="staff-password-123")
        for route_name in ("products_list", "transactions_list", "inventory_report", "dashboard"):
            response = self.client.get(reverse(route_name))
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "صنف قائد سري")
        response = self.client.get(reverse("product_detail", args=[self.restricted.pk]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("leadership_items_list"))
        self.assertEqual(response.status_code, 404)

    def test_only_designated_leader_can_view_restricted_section(self):
        self.client.login(username="auditor", password="audit-password-123")
        self.assertEqual(self.client.get(reverse("leadership_items_list")).status_code, 404)
        self.client.login(username="leader", password="leader-password-123")
        response = self.client.get(reverse("leadership_items_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "صنف قائد سري")
