from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration 0026: v2 Leadership Isolation Fields
    - Adds is_leader_only to Warehouse, Partner, Category
    - Adds is_archived and barcode to Product
    - Adds old_quantity, new_quantity to ActivityLog
    - Adds db_index on ActivityLog(product, created_at) and InventoryTransaction(product, created_at)
    """

    dependencies = [
        ("inventory", "0025_product_is_leadership_restricted_and_more"),
    ]

    operations = [
        # Category: is_leader_only
        migrations.AddField(
            model_name="category",
            name="is_leader_only",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="category leader only",
            ),
        ),
        # Warehouse: is_leader_only
        migrations.AddField(
            model_name="warehouse",
            name="is_leader_only",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="warehouse leader only",
            ),
        ),
        # Partner: is_leader_only
        migrations.AddField(
            model_name="partner",
            name="is_leader_only",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="partner leader only",
            ),
        ),
        # Product: is_archived
        migrations.AddField(
            model_name="product",
            name="is_archived",
            field=models.BooleanField(
                default=False,
                db_index=True,
                verbose_name="archived",
            ),
        ),
        # Product: barcode
        migrations.AddField(
            model_name="product",
            name="barcode",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=50,
                null=True,
                verbose_name="barcode",
            ),
        ),
        # ActivityLog: old_quantity
        migrations.AddField(
            model_name="activitylog",
            name="old_quantity",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="qty before"),
        ),
        # ActivityLog: new_quantity
        migrations.AddField(
            model_name="activitylog",
            name="new_quantity",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="qty after"),
        ),
        # Composite index on ActivityLog(product, created_at)
        migrations.AddIndex(
            model_name="activitylog",
            index=models.Index(fields=["product", "created_at"], name="inv_actlog_prod_date_idx"),
        ),
        # Composite index on InventoryTransaction(product, created_at)
        migrations.AddIndex(
            model_name="inventorytransaction",
            index=models.Index(fields=["product", "created_at"], name="inv_trans_prod_date_idx"),
        ),
    ]
