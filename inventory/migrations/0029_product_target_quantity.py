from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_alter_activitylog_action_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='target_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
