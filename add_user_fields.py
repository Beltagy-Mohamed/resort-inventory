import os
import re

path = r'g:\client_delivery\inventory\models.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Add user to ActivityLog
act_idx = c.find('class ActivityLog(models.Model):')
if 'user = models.ForeignKey' not in c[act_idx:act_idx+300]:
    c = c.replace(
        'class ActivityLog(models.Model):',
        'class ActivityLog(models.Model):\n    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")'
    )

inv_idx = c.find('class InventoryTransaction(models.Model):')
if 'user = models.ForeignKey' not in c[inv_idx:inv_idx+300]:
    c = c.replace(
        'class InventoryTransaction(models.Model):',
        'class InventoryTransaction(models.Model):\n    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")'
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
