import pytest
from inventory.middleware import get_client_ip
from django.test import RequestFactory

def test_get_client_ip_with_x_forwarded_for():
    factory = RequestFactory()
    request = factory.get('/', HTTP_X_FORWARDED_FOR='192.168.1.1, 10.0.0.1')
    ip = get_client_ip(request)
    assert ip == '192.168.1.1'
    
def test_get_client_ip_with_remote_addr():
    factory = RequestFactory()
    request = factory.get('/', REMOTE_ADDR='10.0.0.2')
    ip = get_client_ip(request)
    assert ip == '10.0.0.2'
