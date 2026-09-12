from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category, Color, Size, Product, InventoryTransaction, ActivityLog

def log_activity(action, desc, product=None):
    ActivityLog.objects.create(
        action=action,
        description=desc,
        product=product
    )

# --- Category ---
@receiver(post_save, sender=Category)
def category_saved(sender, instance, created, **kwargs):
    if created:
        log_activity('ADD', f'تم إضافة فئة جديدة: {instance.name}')
    else:
        log_activity('EDIT', f'تم تعديل الفئة: {instance.name}')

@receiver(post_delete, sender=Category)
def category_deleted(sender, instance, **kwargs):
    log_activity('DELETE', f'تم حذف الفئة: {instance.name}')

# --- Color ---
@receiver(post_save, sender=Color)
def color_saved(sender, instance, created, **kwargs):
    if created:
        log_activity('ADD', f'تم إضافة لون جديد: {instance.name}')
    else:
        log_activity('EDIT', f'تم تعديل اللون: {instance.name}')

@receiver(post_delete, sender=Color)
def color_deleted(sender, instance, **kwargs):
    log_activity('DELETE', f'تم حذف اللون: {instance.name}')

# --- Size ---
@receiver(post_save, sender=Size)
def size_saved(sender, instance, created, **kwargs):
    if created:
        log_activity('ADD', f'تم إضافة مقاس جديد: {instance.name}')
    else:
        log_activity('EDIT', f'تم تعديل المقاس: {instance.name}')

@receiver(post_delete, sender=Size)
def size_deleted(sender, instance, **kwargs):
    log_activity('DELETE', f'تم حذف المقاس: {instance.name}')

# --- User ---
@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    if created:
        log_activity('ADD', f'تم إضافة مستخدم جديد: {instance.username}')
    else:
        update_fields = kwargs.get('update_fields')
        if update_fields and 'last_login' in update_fields:
            return
        log_activity('EDIT', f'تم تعديل المستخدم: {instance.username}')

@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    log_activity('DELETE', f'تم حذف المستخدم: {instance.username}')

# --- Product ---
@receiver(post_save, sender=Product)
def product_saved(sender, instance, created, **kwargs):
    if created:
        log_activity('ADD', f'تم إضافة منتج جديد: {instance.name} ({instance.product_code})', product=instance)
    else:
        log_activity('EDIT', f'تم تعديل بيانات المنتج: {instance.name} ({instance.product_code})', product=instance)

@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    log_activity('DELETE', f'تم حذف المنتج: {instance.name} ({instance.product_code})')

# --- InventoryTransaction ---
@receiver(post_save, sender=InventoryTransaction)
def transaction_saved(sender, instance, created, **kwargs):
    action_type = instance.transaction_type # IN, OUT, ADJUST
    if created:
        log_activity(action_type, f'حركة مخزنية جديدة ({action_type}): {instance.quantity} وحدة للمنتج {instance.product.name}', product=instance.product)
    else:
        log_activity(action_type, f'تعديل حركة مخزنية ({action_type}): أصبحت {instance.quantity} وحدة للمنتج {instance.product.name}', product=instance.product)

@receiver(post_delete, sender=InventoryTransaction)
def transaction_deleted(sender, instance, **kwargs):
    action_type = instance.transaction_type
    log_activity('DELETE', f'تم حذف حركة مخزنية ({action_type}) للمنتج {instance.product.name}')
