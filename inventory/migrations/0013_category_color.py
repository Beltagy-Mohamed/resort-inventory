from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0012_systemsettings_alter_activitylog_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="color",
            field=models.CharField(
                default="#3A5457",
                help_text="Hex color used in dashboard charts.",
                max_length=7,
                validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$")],
            ),
        ),
    ]