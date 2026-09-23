from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator


class PublicCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_leader_only=False)

class PublicWarehouseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_leader_only=False)

class PublicPartnerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_leader_only=False)

class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_leadership_restricted=False)

class PublicInventoryTransactionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(product__is_leadership_restricted=False)

class PublicStockManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(product__is_leadership_restricted=False)

class PublicActivityLogManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            Q(product__isnull=True) | Q(product__is_leadership_restricted=False)
        )

class Category(models.Model):
    name = models.CharField(max_length=100)
    is_leader_only = models.BooleanField(default=False, db_index=True, verbose_name='category leader only')
    color = models.CharField(max_length=7, default='#3A5457',
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$')],
        help_text='Hex color used in dashboard charts.')
    objects     = PublicCategoryManager()
    all_objects = models.Manager()
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class SystemSettings(models.Model):
    company_name = models.CharField(max_length=150, default='My Company')
    currency     = models.CharField(max_length=10, default='EGP')
    updated_at   = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.company_name
    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

class Warehouse(models.Model):
    name     = models.CharField(max_length=150, unique=True)
    location = models.CharField(max_length=250, blank=True, null=True)
    manager  = models.CharField(max_length=150, blank=True, null=True)
    is_leader_only = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects     = PublicWarehouseManager()
    all_objects = models.Manager()
    def __str__(self):
        return self.name

class Partner(models.Model):
    PARTNER_TYPES = [('SUPPLIER', 'مورد'), ('CLIENT', 'عميل'), ('OTHER', 'أخرى')]
    name         = models.CharField(max_length=200)
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, default='CLIENT')
    contact_info = models.TextField(blank=True, null=True)
    is_leader_only = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects     = PublicPartnerManager()
    all_objects = models.Manager()
    def __str__(self):
        return self.name

class LeadershipAccessConfig(models.Model):
    id     = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    holder = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='leadership_access')
    granted_at      = models.DateTimeField(auto_now_add=True)
    granted_by_note = models.CharField(max_length=255)
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'Leadership Access Config'
        verbose_name_plural = 'Leadership Access Configs'

class LeadershipAccessLog(models.Model):
    ACTION_CHOICES = [
        ('VIEW_LIST','view list'),('VIEW_DETAIL','view detail'),
        ('CREATE','create'),('UPDATE','update'),('DELETE','delete'),
        ('EXPORT','export'),('TRANSACTION','transaction'),
    ]
    user       = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    action     = models.CharField(max_length=20, choices=ACTION_CHOICES)
    product    = models.ForeignKey('Product', null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

class Product(models.Model):
    is_leadership_restricted = models.BooleanField(default=False, db_index=True)
    is_archived = models.BooleanField(default=False, db_index=True)
    objects     = ProductManager()
    all_objects = models.Manager()
    name          = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    color    = models.ForeignKey(Color,    on_delete=models.SET_NULL, null=True, blank=True)
    size     = models.ForeignKey(Size,     on_delete=models.SET_NULL, null=True, blank=True)
    cost_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity      = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)
    target_quantity = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey("Partner", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="الشركة الموردة", related_name="supplied_products")
    barcode     = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out'
        elif self.quantity <= self.minimum_stock:
            return 'low'
        return 'available'
    @property
    def stock_status_text(self):
        if self.quantity == 0:
            return 'out'
        elif self.quantity <= self.minimum_stock:
            return 'low'
        return 'available'
    def __str__(self):
        return self.name

class Stock(models.Model):
    objects     = PublicStockManager()
    all_objects = models.Manager()
    product   = models.ForeignKey(Product,   on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks')
    quantity  = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ('product', 'warehouse')
    def __str__(self):
        return self.product.name + ' in ' + self.warehouse.name

class InventoryTransaction(models.Model):
    objects     = PublicInventoryTransactionManager()
    all_objects = models.Manager()
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    TRANSACTION_TYPES = [('IN','إستلام / وارد'), ('OUT','صرف / صادر'), ('ADJUST','تسوية / جرد')]
    product          = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    warehouse  = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transactions')
    partner    = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity   = models.PositiveIntegerField()
    notes      = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['product','created_at'])]
    def __str__(self):
        return str(self.product_id) + ' - ' + self.transaction_type

class ActivityLog(models.Model):
    @property
    def diff_quantity(self):
        if self.new_quantity is not None and self.old_quantity is not None:
            diff = self.new_quantity - self.old_quantity
            if diff > 0:
                return f"+{diff}"
            return str(diff)
        return "-"

    objects     = PublicActivityLogManager()
    all_objects = models.Manager()
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    ACTIONS = [('ADD','إضافة'),('EDIT','تعديل'),('DELETE','حذف'),('IN','استلام'),('OUT','صرف'),('ADJUST','تسوية')]
    action       = models.CharField(max_length=20, choices=ACTIONS)
    product      = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    old_quantity = models.PositiveIntegerField(null=True, blank=True)
    new_quantity = models.PositiveIntegerField(null=True, blank=True)
    description  = models.CharField(max_length=255)
    created_at   = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['product','created_at'])]
    def __str__(self):
        return self.description
