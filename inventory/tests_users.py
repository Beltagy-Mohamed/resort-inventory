from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Product

class UserManagementTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpassword'
        )
        self.normal_user = User.objects.create_user(
            username='cashier',
            email='cashier@test.com',
            password='cashierpassword'
        )
        product_ct = ContentType.objects.get_for_model(Product)
        self.add_product_perm = Permission.objects.get(content_type=product_ct, codename='add_product')

    def test_users_list_access_superuser_only(self):
        self.client.login(username='cashier', password='cashierpassword')
        response = self.client.get(reverse('users_list'))
        self.assertNotEqual(response.status_code, 200)
        
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('users_list'))
        self.assertEqual(response.status_code, 200)

    def test_add_user_with_permissions(self):
        self.client.login(username='admin', password='adminpassword')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'perm_inventory': 'on'
        }
        response = self.client.post(reverse('add_user'), data)
        self.assertEqual(response.status_code, 302)
        
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.has_perm('inventory.add_product'))

    def test_sidebar_hides_add_product_button(self):
        self.client.login(username='cashier', password='cashierpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(reverse('add_product'), str(response.content))
        
        self.normal_user.user_permissions.add(self.add_product_perm)
        response = self.client.get(reverse('dashboard'))
        self.assertIn(reverse('add_product'), str(response.content))
