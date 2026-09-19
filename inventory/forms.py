from django import forms
from .models import Product, Warehouse, Partner, Category, Color, Size, InventoryTransaction, SystemSettings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from inventory.decorators import is_the_leader
import re

class StripWhitespaceMixin:
    def clean(self):
        cleaned_data = super().clean()
        for field, value in list(cleaned_data.items()):
            if isinstance(value, str):
                stripped_val = value.strip()
                cleaned_data[field] = stripped_val
                
                if not stripped_val and self.fields[field].required:
                    self.add_error(field, "هذا الحقل لا يمكن أن يكون فارغاً أو يحتوي على مسافات فقط.")
                    continue
                
                if stripped_val and re.search(r'[<>`{}]', stripped_val):
                    self.add_error(field, "يحتوي النص على رموز غير مسموحة لحماية النظام.")
        return cleaned_data

    def clean_positive_numbers(self, cleaned_data, fields_to_check):
        for field in fields_to_check:
            val = cleaned_data.get(field)
            if val is not None and val < 0:
                self.add_error(field, ValidationError("القيمة لا يمكن أن تكون سالبة."))

class ProductForm(StripWhitespaceMixin, forms.ModelForm):
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label='-- اختر المخزن --',
        label="المخزن (الرصيد الافتتاحي)",
        help_text="سيتم إيداع الكمية الافتتاحية في هذا المخزن."
    )
    partner = forms.ModelChoiceField(
        queryset=Partner.objects.all(),
        required=False,
        empty_label='-- بدون جهة (رصيد افتتاحي فقط) --',
        label="المورد / الجهة (اختياري)",
        help_text="اختر المورد إذا أردت ربط هذه الكمية بكشف حسابه."
    )

    class Meta:
        model = Product
        fields = [
            "name", "category", "color", "size",
            "cost_price", "selling_price", "quantity", 
            "minimum_stock", "is_leadership_restricted", "description"
        ]
        labels = {
            "name": "اسم المنتج",
            "category": "الفئة",
            "color": "اللون",
            "size": "المقاس",
            "cost_price": "سعر التكلفة",
            "selling_price": "سعر البيع",
            "quantity": "الرصيد الافتتاحي (كمية)",
            "description": "وصف المنتج",
            "minimum_stock": "حد التنبيه للمخزون",
            "is_leadership_restricted": "صنف خاص بالقائد (سري)",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "مثال: قميص قطن"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "color": forms.Select(attrs={"class": "form-control"}),
            "size": forms.Select(attrs={"class": "form-control"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-control"}),
            "selling_price": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "minimum_stock": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "is_leadership_restricted": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        is_leader = kwargs.pop('is_leader', False)
        super().__init__(*args, **kwargs)
        
        if is_leader:
            if 'warehouse' in self.fields:
                self.fields['warehouse'].queryset = Warehouse.all_objects.all()
            if 'partner' in self.fields:
                self.fields['partner'].queryset = Partner.all_objects.all()
            if 'category' in self.fields:
                self.fields['category'].queryset = Category.all_objects.all()
        else:
            if 'is_leadership_restricted' in self.fields:
                self.fields.pop('is_leadership_restricted')
                
        if self.instance and self.instance.pk:
            self.fields['quantity'].disabled = True
            self.fields['quantity'].help_text = "لا يمكن تعديل الرصيد الافتتاحي بعد الإضافة."
            if 'warehouse' in self.fields:
                del self.fields['warehouse']
        else:
            self.fields['quantity'].help_text = "الكمية المتاحة حالياً."
        
        for field_name in ['category', 'color', 'size', 'warehouse']:
            if field_name in self.fields:
                field = self.fields[field_name]
                field.empty_label = f'-- بدون {field.label.split()[0]} --'

class CategoryForm(StripWhitespaceMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "color"]
        labels = {"name": "اسم الفئة", "color": "اللون"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "اسم الفئة"}),
            "color": forms.TextInput(attrs={"class": "form-control category-color-input", "type": "color"}),
        }

class ColorForm(StripWhitespaceMixin, forms.ModelForm):
    class Meta:
        model = Color
        fields = ["name"]
        labels = {"name": "اسم اللون"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "اسم اللون"})
        }

class SizeForm(StripWhitespaceMixin, forms.ModelForm):
    class Meta:
        model = Size
        fields = ["name"]
        labels = {"name": "اسم المقاس"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "اسم المقاس"})
        }

class InventoryTransactionForm(StripWhitespaceMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and (user.is_superuser or is_the_leader(user)):
            # Leader/superuser: see all products, warehouses, partners
            self.fields['product'].queryset = Product.all_objects.filter(is_archived=False).order_by('name')
            self.fields['warehouse'].queryset = Warehouse.all_objects.all().order_by('name')
            self.fields['partner'].queryset = Partner.all_objects.all().order_by('name')
        else:
            # Regular user: only public (non-leader-restricted) items
            self.fields['product'].queryset = Product.objects.filter(is_archived=False).order_by('name')
            self.fields['warehouse'].queryset = Warehouse.objects.all().order_by('name')
            self.fields['partner'].queryset = Partner.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        self.clean_positive_numbers(cleaned_data, ['quantity', 'unit_price'])
        qty = cleaned_data.get('quantity')
        if qty is not None and qty == 0:
            self.add_error('quantity', ValidationError("الكمية لا يمكن أن تكون صفراً."))
        return cleaned_data

    class Meta:
        model = InventoryTransaction
        fields = ["product", "warehouse", "partner", "transaction_type", "quantity", "unit_price", "notes"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "warehouse": forms.Select(attrs={"class": "form-control"}),
            "partner": forms.Select(attrs={"class": "form-control"}),
            "transaction_type": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4})
        }

class WarehouseForm(StripWhitespaceMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not (user.is_superuser or is_the_leader(user)):
            self.fields.pop('is_leader_only', None)

    class Meta:
        model = Warehouse
        fields = ["name", "location", "manager", "is_leader_only"]
        labels = {
            "name": "اسم المخزن",
            "location": "العنوان / الموقع",
            "manager": "أمين المخزن",
            "is_leader_only": "مخزن سري خاص بالقائد فقط",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "manager": forms.TextInput(attrs={"class": "form-control"}),
            "is_leader_only": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "manager": forms.TextInput(attrs={"class": "form-control"}),
        }

class PartnerForm(StripWhitespaceMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not (user.is_superuser or is_the_leader(user)):
            self.fields.pop('is_leader_only', None)

    class Meta:
        model = Partner
        fields = ["name", "partner_type", "contact_info", "is_leader_only"]
        labels = {
            "name": "اسم الجهة",
            "partner_type": "نوع الجهة",
            "contact_info": "معلومات التواصل (هاتف..)",
            "is_leader_only": "جهة سرية خاصة بالقائد فقط",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "partner_type": forms.Select(attrs={"class": "form-control"}),
            "contact_info": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_leader_only": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "partner_type": forms.Select(attrs={"class": "form-control"}),
            "contact_info": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ["company_name", "currency"]
        labels = {
            "company_name": "اسم الشركة",
            "currency": "العملة",
        }
        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "currency": forms.TextInput(attrs={"class": "form-control", "placeholder": "مثال: EGP"}),
        }

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="الاسم الأول", max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="اسم العائلة", max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    perm_inventory = forms.BooleanField(label="إدارة المخزون (إضافة/تعديل المنتجات)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_sales = forms.BooleanField(label="إدارة المبيعات (حركات مخزنية)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_reports = forms.BooleanField(label="التقارير (رؤية الأرباح وتقارير الجرد)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_delete = forms.BooleanField(label="صلاحية الحذف (حذف المنتجات والحركات)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    is_leader = forms.BooleanField(label="تخصيص كقائد (الوصول لمنتجات وأصناف القائد السري)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_superadmin = forms.BooleanField(label="مدير نظام رئيسي (Superuser) - له جميع الصلاحيات", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name'    )

class CustomUserEditForm(forms.ModelForm):
    perm_inventory = forms.BooleanField(label='صلاحيات المخزون (منتجات/حركات)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_sales = forms.BooleanField(label='صلاحيات المبيعات (نقطة البيع)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_reports = forms.BooleanField(label='صلاحيات التقارير (عرض طباعة/تصدير)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_delete = forms.BooleanField(label='صلاحيات الحذف (حذف المنتجات/الحركات)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    is_leader = forms.BooleanField(label="تخصيص كقائد (الوصول لمنتجات وأصناف القائد السري)", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_superadmin = forms.BooleanField(label="مدير نظام رئيسي (Superuser) - له جميع الصلاحيات", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_active')

    def __init__(self, *args, **kwargs):
        is_leader = kwargs.pop('is_leader', False)
        super().__init__(*args, **kwargs)
        
        if is_leader:
            if 'warehouse' in self.fields:
                self.fields['warehouse'].queryset = Warehouse.all_objects.all()
            if 'partner' in self.fields:
                self.fields['partner'].queryset = Partner.all_objects.all()
            if 'category' in self.fields:
                self.fields['category'].queryset = Category.all_objects.all()
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
