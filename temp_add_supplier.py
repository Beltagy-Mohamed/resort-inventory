import re
path = r'E:\خاص مشروع\client_delivery\inventory\models.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if 'supplier = models.ForeignKey(' not in c:
    old = 'target_quantity = models.IntegerField(default=0, verbose_name="الكمية المستهدفة")'
    new = 'target_quantity = models.IntegerField(default=0, verbose_name="الكمية المستهدفة")\n    supplier = models.ForeignKey("Partner", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الشركة الموردة", related_name="supplied_products")'
    c = c.replace(old, new)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
