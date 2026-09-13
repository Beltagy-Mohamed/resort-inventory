import os

path = r'g:\client_delivery\inventory\forms.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target1 = '''class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "location", "is_active"]
        labels = {
            "name": "اسم المخزن",
            "location": "الموقع / العنوان",
            "is_active": "نشط (يعمل)",
        }'''

repl1 = '''class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "location", "manager"]
        labels = {
            "name": "اسم المخزن",
            "location": "الموقع / العنوان",
            "manager": "أمين المخزن",
        }'''

target2 = '''class PartnerForm(forms.ModelForm):
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
        }'''

repl2 = '''class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["name", "partner_type", "contact_info"]
        labels = {
            "name": "اسم الجهة",
            "partner_type": "نوع الجهة",
            "contact_info": "بيانات التواصل (هاتف، عنوان..)",
        }'''

c = c.replace(target1, repl1).replace(target2, repl2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
