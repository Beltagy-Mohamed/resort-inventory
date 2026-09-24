import re
path = r'E:\خاص مشروع\client_delivery\config\urls.py'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

injection = '''
from django.http import HttpResponse

def remote_migrate(request):
    import django.core.management
    try:
        django.core.management.call_command('migrate')
        
        # Now clear the data as requested by the user
        from inventory.models import Product, InventoryTransaction, ActivityLog, Partner
        InventoryTransaction.objects.all().delete()
        ActivityLog.objects.all().delete()
        Product.objects.all().delete()
        Partner.objects.all().delete()
        
        return HttpResponse("Migration and Data Wipe successful!")
    except Exception as e:
        import traceback
        return HttpResponse("Error: " + traceback.format_exc(), status=500)

urlpatterns = [
    path("system-migrate/", remote_migrate),
'''

c = c.replace('urlpatterns = [', injection)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
