from django.db import migrations


CATEGORY_COLORS = [
    "#3A5457",
    "#C19A6B",
    "#2F7D78",
    "#8B5E3C",
    "#3B82F6",
    "#8B5CF6",
    "#D97706",
    "#DC2626",
]


def assign_category_colors(apps, schema_editor):
    Category = apps.get_model("inventory", "Category")
    categories = Category.objects.order_by("id")
    for index, category in enumerate(categories):
        if category.color == "#3A5457":
            category.color = CATEGORY_COLORS[index % len(CATEGORY_COLORS)]
            category.save(update_fields=["color"])


def keep_category_colors(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0013_category_color"),
    ]

    operations = [
        migrations.RunPython(assign_category_colors, keep_category_colors),
    ]
