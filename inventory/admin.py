from django.contrib import admin
from .models import Category, Color, Size, Product, CodeSequence, Warehouse, Partner, Stock
from .models import InventoryTransaction
# from .models import InventoryTransaction
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Product)
admin.site.register(CodeSequence)

# admin.site.register(InventoryTransaction)
admin.site.register(InventoryTransaction)
admin.site.register(Warehouse)
admin.site.register(Partner)
admin.site.register(Stock)
