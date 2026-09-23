import re
path = r'E:\خاص مشروع\client_delivery\inventory\views\settings.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

wipe_view = '''
def wipe_all_data_secret(request):
    from django.http import HttpResponse
    from inventory.models import Product, InventoryTransaction, ActivityLog, Partner
    
    InventoryTransaction.objects.all().delete()
    ActivityLog.objects.all().delete()
    Product.objects.all().delete()
    Partner.objects.all().delete()
    
    return HttpResponse("All Products, Transactions, Activity Logs, and Partners have been completely deleted from the database. You can now re-upload your Excel file.")
'''

if 'wipe_all_data_secret' not in c:
    c += wipe_view
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

# Now add it to urls.py
url_path = r'E:\خاص مشروع\client_delivery\inventory\urls.py'
with open(url_path, 'r', encoding='utf-8') as f:
    u = f.read()

if 'wipe_all_data_secret' not in u:
    # insert before urlpatterns = [
    u = u.replace('urlpatterns = [', 'urlpatterns = [\n    path("wipe-all-data-secret-12345/", views.settings.wipe_all_data_secret, name="wipe_all_data_secret"),')
    with open(url_path, 'w', encoding='utf-8') as f:
        f.write(u)
