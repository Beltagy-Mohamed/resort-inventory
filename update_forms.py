import os

path = r'g:\client_delivery\inventory\forms.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Make sure Warehouse and Partner are imported
if 'from .models import Warehouse' not in c:
    c = c.replace('from .models import Product', 'from .models import Product\nfrom .models import Warehouse, Partner')

new_forms = '''

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "location", "is_active"]
        labels = {
            "name": "اسم المخزن",
            "location": "الموقع / العنوان",
            "is_active": "نشط (يعمل)",
        }


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["name", "partner_type", "phone", "email", "address", "is_active"]
        labels = {
            "name": "اسم الجهة",
            "partner_type": "نوع الجهة",
            "phone": "رقم الهاتف",
            "email": "البريد الإلكتروني",
            "address": "العنوان",
            "is_active": "نشط",
        }
'''

if 'class WarehouseForm' not in c:
    c += new_forms

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
