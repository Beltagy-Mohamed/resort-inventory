import os
import re

path = r'g:\client_delivery\inventory\signals.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'def log_activity(action, desc, product=None):',
    '''from .middleware import get_current_user

def log_activity(action, desc, product=None):
    user = get_current_user()
    if user and not user.is_authenticated:
        user = None'''
)

c = c.replace(
    '        product=product\n    )',
    '        product=product,\n        user=user\n    )'
)

# Also update InventoryTransaction pre_save to inject user if missing
if 'def transaction_pre_save' not in c:
    c += '''
@receiver(pre_save, sender=InventoryTransaction)
def transaction_pre_save(sender, instance, **kwargs):
    if not instance.user_id:
        user = get_current_user()
        if user and user.is_authenticated:
            instance.user = user
'''
    c = c.replace('from django.db.models.signals import post_save, post_delete', 'from django.db.models.signals import pre_save, post_save, post_delete')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
