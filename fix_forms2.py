import os

path = r'g:\client_delivery\inventory\forms.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('"price",', '"cost_price",\n            "selling_price",')
c = c.replace('"price": _("Price"),', '"cost_price": "سعر الشراء / التكلفة",\n            "selling_price": "سعر البيع / التوريد",')
c = c.replace('"price": forms.NumberInput(', '"cost_price": forms.NumberInput(attrs={"class": "form-control"}),\n            "selling_price": forms.NumberInput(')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
