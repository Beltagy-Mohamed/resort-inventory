import os
import re

path = r'g:\client_delivery\inventory\models.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('''    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True, # temporarily nullable for old data migration
    )''', 
'''    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="المخزن",
    )''')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
