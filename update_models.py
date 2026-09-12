import os
import re

path = r'g:\client_delivery\inventory\models.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add Warehouse, Partner, Stock models before Product
new_models = '''
class Warehouse(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="اسم المخزن")
    location = models.CharField(max_length=250, blank=True, null=True, verbose_name="الموقع/العنوان")
    manager = models.CharField(max_length=150, blank=True, null=True, verbose_name="أمين المخزن")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Partner(models.Model):
    PARTNER_TYPES = [
        ("SUPPLIER", "مورد"),
        ("CLIENT", "عميل / جهة صرف"),
        ("OTHER", "جهة أخرى"),
    ]
    name = models.CharField(max_length=200, verbose_name="اسم الجهة")
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, default="CLIENT", verbose_name="نوع الجهة")
    contact_info = models.TextField(blank=True, null=True, verbose_name="بيانات التواصل")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_partner_type_display()})"
'''

c = c.replace('class Product(models.Model):', new_models + '\n\nclass Product(models.Model):')

# 2. Modify Product: price -> selling_price, add cost_price
# Note: Since Vercel deployments crash if DB schema doesn't match models,
# we need to be careful. I will add cost_price, and rename price to selling_price.
c = c.replace('    price = models.DecimalField(\n        max_digits=10,\n        decimal_places=2,\n    )', 
'''    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="سعر الشراء/التكلفة"
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="سعر البيع"
    )''')

# 3. Add Stock model after Product
stock_model = '''
class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} in {self.warehouse.name}: {self.quantity}"
'''
c = c.replace('class InventoryTransaction(models.Model):', stock_model + '\n\nclass InventoryTransaction(models.Model):')


# 4. Modify InventoryTransaction: Add warehouse, partner, unit_price
trans_fields = '''    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True, # temporarily nullable for old data migration
    )

    partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الجهة (المورد / العميل)",
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="السعر وقت الحركة",
    )'''

c = c.replace('    quantity = models.PositiveIntegerField()', trans_fields + '\n\n    quantity = models.PositiveIntegerField()')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
