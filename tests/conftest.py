import pytest
from pytest_factoryboy import register
from .factories import UserFactory, GroupFactory, CategoryFactory, WarehouseFactory, PartnerFactory, ProductFactory
from django.contrib.auth.models import Permission

register(UserFactory)
register(GroupFactory)
register(CategoryFactory)
register(WarehouseFactory)
register(PartnerFactory)
register(ProductFactory)

@pytest.fixture
def api_client():
    from django.test import Client
    return Client()

@pytest.fixture
def leader_user(db, user_factory, group_factory):
    user = user_factory(username="leader_user")
    group, _ = group_factory._meta.model.objects.get_or_create(name="Leader")
    user.groups.add(group)
    
    # Add view permissions
    perms = Permission.objects.filter(codename__in=['view_product', 'view_warehouse', 'view_partner', 'add_product', 'change_product'])
    user.user_permissions.add(*perms)
    return user

@pytest.fixture
def superuser(db, user_factory):
    return user_factory(username="superuser", is_superuser=True)

@pytest.fixture
def regular_user(db, user_factory):
    user = user_factory(username="regular_user", is_superuser=False)
    # Give them all basic inventory permissions
    perms = Permission.objects.filter(content_type__app_label='inventory')
    user.user_permissions.add(*perms)
    return user
