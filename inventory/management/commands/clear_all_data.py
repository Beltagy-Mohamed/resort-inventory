from django.core.management.base import BaseCommand
from inventory.models import Product, Category, Color, Size, Warehouse, Partner, InventoryTransaction, Stock, ActivityLog

class Command(BaseCommand):
    help = 'Clears all operational data from the database but keeps users and settings.'

    def handle(self, *args, **options):
        self.stdout.write("Deleting ActivityLogs...")
        ActivityLog.objects.all().delete()
        
        self.stdout.write("Deleting InventoryTransactions...")
        InventoryTransaction.all_objects.all().delete()
        
        self.stdout.write("Deleting Stocks...")
        Stock.all_objects.all().delete()
        
        self.stdout.write("Deleting Products...")
        Product.all_objects.all().delete()
        
        self.stdout.write("Deleting Categories, Colors, Sizes...")
        Category.objects.all().delete()
        Color.objects.all().delete()
        Size.objects.all().delete()
        
        self.stdout.write("Deleting Partners...")
        Partner.all_objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully cleared all operational data!'))
