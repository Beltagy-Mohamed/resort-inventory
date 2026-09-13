from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class Category(models.Model):

    name = models.CharField(max_length=100)

    color = models.CharField(
        max_length=7,
        default="#3A5457",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$")],
        help_text="Hex color used in dashboard charts.",
    )

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
    """
    A single row holding system-wide settings. Deliberately minimal —
    just what's actually useful for a small inventory system, not a
    generic settings framework.
    """

    company_name = models.CharField(
        max_length=150,
        default="My Company",
    )

    currency = models.CharField(
        max_length=10,
        default="EGP",
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.company_name

    @classmethod
    def load(cls):
        """
        Returns the single settings row, creating it with defaults the
        first time it's needed. Callers never have to worry about
        whether a row exists yet.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj



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


class Product(models.Model):



    name = models.CharField(
        max_length=200
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    cost_price = models.DecimalField(
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
    )

    quantity = models.PositiveIntegerField(
        default=0
    )

    minimum_stock = models.PositiveIntegerField(
        default=5
    )

    description = models.TextField(
        blank=True
    )





    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def stock_status(self):

        if self.quantity == 0:
            return "out"

        elif self.quantity <= self.minimum_stock:
            return "low"

        return "available"

    @property
    def stock_status_text(self):

        if self.quantity == 0:
            return "نفد"

        elif self.quantity <= self.minimum_stock:
            return "منخفض"

        return "متوفر"

    def __str__(self):
        return self.name



class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} in {self.warehouse.name}: {self.quantity}"


class InventoryTransaction(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")

    TRANSACTION_TYPES = [

        ("IN", _("Received")),

        ("OUT", _("Issued")),

        ("ADJUST", _("Adjustment")),

    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="المخزن",
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
    )

    quantity = models.PositiveIntegerField()

    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Inventory Transaction"

        verbose_name_plural = "Inventory Transactions"

    def __str__(self):

        return f"{self.product.product_code} - {self.transaction_type}"

    # NOTE: this model intentionally has NO save() override.
    # Stock mutation is handled exclusively by InventoryService.process().
    # A previous version of save() also mutated Product.quantity here,
    # which caused every transaction to be applied twice when combined
    # with InventoryService. Do not re-add stock logic to this model.


class ActivityLog(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")

    ACTIONS = [

        ("ADD", _("Add")),

        ("EDIT", _("Edit")),

        ("DELETE", _("Delete")),

        ("IN", "استلام"),

        ("OUT", "صرف"),

        ("ADJUST", "جرد"),

    ]

    action = models.CharField(
        max_length=20,
        choices=ACTIONS,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    description = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

    def __str__(self):

        return self.description