import os
import re

path = r'g:\client_delivery\inventory\forms.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        fields = [

            "product",

            "transaction_type",

            "quantity",

            "notes",

        ]'''

repl = '''        fields = [
            "product",
            "warehouse",
            "partner",
            "transaction_type",
            "quantity",
            "unit_price",
            "notes",
        ]'''

c = c.replace(target, repl)

target_widgets = '''            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),'''

repl_widgets = '''            "warehouse": forms.Select(attrs={"class": "form-control"}),
            "partner": forms.Select(attrs={"class": "form-control"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),'''

c = c.replace(target_widgets, repl_widgets)

target_labels = '''            "quantity": _("Quantity"),

            "notes": _("Notes"),

        }'''

repl_labels = '''            "quantity": _("Quantity"),
            "warehouse": "المخزن",
            "partner": "الجهة (عميل / مورد)",
            "unit_price": "السعر (للوحدة)",
            "notes": _("Notes"),
        }'''

c = c.replace(target_labels, repl_labels)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
