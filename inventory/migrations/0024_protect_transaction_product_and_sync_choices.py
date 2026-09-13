from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("inventory", "0023_delete_codesequence")]

    operations = [
        migrations.AlterField(
            model_name="activitylog",
            name="action",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("ADD", "أضف"), ("EDIT", "تعديل"), ("DELETE", "حذف"),
                    ("IN", "استلام"), ("OUT", "صرف"), ("ADJUST", "جرد"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="inventorytransaction",
            name="transaction_type",
            field=models.CharField(
                max_length=10,
                choices=[("IN", "استلام"), ("OUT", "صرف"), ("ADJUST", "جرد")],
            ),
        ),
        migrations.AlterField(
            model_name="inventorytransaction",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="transactions",
                to="inventory.product",
            ),
        ),
    ]
