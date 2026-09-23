from django.http import HttpResponse
from django.core.management import call_command

def remote_setup(request):
    try:
        # Run migrations
        call_command('migrate', interactive=False)
        
        # Clear data
        from inventory.models import Product, InventoryTransaction, ActivityLog, Partner
        InventoryTransaction.all_objects.all().delete()
        ActivityLog.objects.all().delete()
        Product.all_objects.all().delete()
        Partner.objects.all().delete()
        
        return HttpResponse("✅ Successfully migrated remote database and cleared all data.")
    except Exception as e:
        return HttpResponse(f"❌ Error during remote setup: {str(e)}")
