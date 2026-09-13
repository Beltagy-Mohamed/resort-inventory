from django import forms
from .models import Product
from .models import Warehouse, Partner
from .models import Category
from .models import Color
from .models import InventoryTransaction
from .models import Size
from .models import SystemSettings

from django.core.exceptions import ValidationError

class StripWhitespaceMixin:
    def clean(self):
        cleaned_data = super().clean()
        for field, value in cleaned_data.items():
            if isinstance(value, str):
                stripped = value.strip()
                if not stripped and self.fields[field].required:
                    self.add_error(field, ValidationError("هذا الحقل لا يمكن أن يكون فارغاً أو مجرد مسافات."))
                cleaned_data[field] = stripped
        return cleaned_data
        
    def clean_positive_numbers(self, cleaned_data, fields):
        for field in fields:
            val = cleaned_data.get(field)
            if val is not None and val < 0:
                self.add_error(field, ValidationError("القيمة لا يمكن أن تكون سالبة."))

class ProductForm(StripWhitespaceMixin, forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        self.clean_positive_numbers(cleaned_data, ['cost_price', 'selling_price', 'quantity', 'minimum_stock'])
        return cleaned_data


    
    initial_warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        label="المخزن (للرصيد الافتتاحي)",
        help_text="المخزن الذي سيتم إضافة هذه الكمية إليه."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Editing existing product
            if 'initial_warehouse' in self.fields:
                self.fields.pop('initial_warehouse')
            if 'quantity' in self.fields:
                self.fields['quantity'].widget.attrs['readonly'] = True
                self.fields['quantity'].help_text = "لتعديل الكمية قم بعمل حركة استلام أو صرف أو جرد."
        else:
            # Adding new product
            if 'quantity' in self.fields:
                self.fields['quantity'].help_text = "الرصيد الافتتاحي للمنتج."

    class Meta:

        model = Product

        fields = [
            "name",
            "category",
            "color",
            "size",
            "cost_price",
            "selling_price",
            "quantity",
            "minimum_stock",
            "description",
        ]
        labels = {
            "name": "اسم المنتج",
            "category": "الفئة",
            "color": "اللون",
            "size": "المقاس",
            "cost_price": "سعر التكلفة",
            "selling_price": "سعر البيع",
            "quantity": "الكمية المتاحة",
            "minimum_stock": "الحد الأدنى للمخزون",
            "description": "الوصف",
        }
        labels = {
            "name": "اسم المنتج",
            "category": "الفئة",
            "color": "اللون",
            "size": "المقاس",
            "cost_price": "سعر التكلفة",
            "selling_price": "سعر البيع",
            "quantity": "الكمية المتاحة",
            "minimum_stock": "الحد الأدنى للمخزون",
            "description": "الوصف",
        }

        labels = {
            "name": "اسم المنتج",
            "category": "الفئة",
            "color": "اللون",
            "size": "Size",
            "cost_price": "سعر الشراء / التكلفة",
            "selling_price": "سعر البيع / التوريد",
            "quantity": "الكمية",
            "description": "الوصف",
            "minimum_stock": "الحد الأدنى للمخزون",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "category": forms.Select(
                attrs={"class": "form-control"}
            ),
            "color": forms.Select(
                attrs={"class": "form-control"}
            ),
            "size": forms.Select(
                attrs={"class": "form-control"}
            ),
            "cost_price": forms.NumberInput(attrs={"class": "form-control"}),
            "selling_price": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "minimum_stock": forms.NumberInput(
            attrs={"class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),
        }
class CategoryForm(StripWhitespaceMixin, forms.ModelForm):

    class Meta:

        model = Category

        fields = [
            "name",
            "color",
        ]
        labels = {
            "name": "اسم اللون",
            "color": "اللون",
        }
        labels = {
            "name": "اسم الفئة",
            "color": "اللون",
        }

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "اسم الفئة"
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control category-color-input",
                    "type": "color",
                }
            ),

        }        
        
class ColorForm(StripWhitespaceMixin, forms.ModelForm):

    class Meta:

        model = Color

        fields = [
            "name",
        ]
        labels = {
            "name": "اسم المقاس",
        }

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "اسم اللون"
                }
            )

        }        
        
class InventoryTransactionForm(StripWhitespaceMixin, forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        self.clean_positive_numbers(cleaned_data, ['quantity', 'unit_price'])
        qty = cleaned_data.get('quantity')
        if qty is not None and qty == 0:
            self.add_error('quantity', ValidationError("الكمية لا يمكن أن تكون صفراً."))
        return cleaned_data


    class Meta:

        model = InventoryTransaction

        fields = [
            "product",
            "warehouse",
            "partner",
            "transaction_type",
            "quantity",
            "unit_price",
            "notes",
        ]

        widgets = {

            "product": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "transaction_type": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            )

        }
        
class SizeForm(StripWhitespaceMixin, forms.ModelForm):

    class Meta:

        model = Size

        fields = [
            "name",
        ]
        labels = {
            "name": "اسم المقاس",
        }

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "اسم المقاس"
                }
            )

        }        

class SystemSettingsForm(forms.ModelForm):

    class Meta:

        model = SystemSettings

        fields = [
            "company_name",
            "currency",
        ]

        labels = {
            "company_name": "اسم الشركة",
            "currency": "العملة",
        }

        widgets = {
            "company_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "currency": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "مثال: EGP"}
            ),
        }


from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="الاسم الأول", max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="الاسم العائلة", max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    perm_inventory = forms.BooleanField(label="إدارة المخزون (إضافة/تعديل المنتجات)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_sales = forms.BooleanField(label="إدارة المبيعات (حركات مخزنية)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_reports = forms.BooleanField(label="التقارير (رؤية الأرباح وتقارير الجرد)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_delete = forms.BooleanField(label="صلاحية الحذف (حذف المنتجات والحركات)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['username'].label = 'اسم المستخدم'
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomUserEditForm(forms.ModelForm):
    password = forms.CharField(label="تغيير كلمة المرور (اتركه فارغاً للإبقاء عليها)", required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="الاسم الأول", max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="اسم العائلة", max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(label="نشط (يمكنه تسجيل الدخول)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    perm_inventory = forms.BooleanField(label="إدارة المخزون (إضافة/تعديل المنتجات)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_sales = forms.BooleanField(label="إدارة المبيعات (حركات مخزنية)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_reports = forms.BooleanField(label="التقارير (رؤية الأرباح وتقارير الجرد)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_delete = forms.BooleanField(label="صلاحية الحذف (حذف المنتجات والحركات)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_active')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['username'].label = 'اسم المستخدم'
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
                
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class WarehouseForm(StripWhitespaceMixin, forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "location", "manager"]
        labels = {
            "name": "اسم المخزن",
            "location": "الموقع / العنوان",
            "manager": "أمين المخزن",
        }


class PartnerForm(StripWhitespaceMixin, forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["name", "partner_type", "contact_info"]
        labels = {
            "name": "اسم الجهة",
            "partner_type": "نوع الجهة",
            "contact_info": "بيانات التواصل (هاتف، عنوان..)",
        }
