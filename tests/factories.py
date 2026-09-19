import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from inventory.models import Category, Warehouse, Partner, Product, InventoryTransaction

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_active = True
    
class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
    name = "Leader"

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f"Category {n}")
    color = "#ffffff"

class WarehouseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Warehouse
    
    name = factory.Sequence(lambda n: f"Warehouse {n}")
    location = "Test Location"
    manager = "Test Manager"
    is_leader_only = False

class PartnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Partner
    
    name = factory.Sequence(lambda n: f"Partner {n}")
    partner_type = "CLIENT"
    contact_info = "123456789"
    is_leader_only = False

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f"Product {n}")
    category = factory.SubFactory(CategoryFactory)
    cost_price = 10.0
    selling_price = 15.0
    quantity = 0
    minimum_stock = 5
    is_leadership_restricted = False
