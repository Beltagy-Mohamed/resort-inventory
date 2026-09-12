from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product
from .models import Category
from .models import Color
from .models import InventoryTransaction
from .models import Size
from .models import SystemSettings
class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            "name",
            "category",
            "color",
            "size",
            "price",
            "quantity",
            "minimum_stock",
            "description",
        ]

        labels = {
            "name": _("Product name"),
            "category": _("Category"),
            "color": _("Color"),
            "size": _("Size"),
            "price": _("Price"),
            "quantity": _("Quantity"),
            "description": _("Description"),
            "minimum_stock": _("Minimum stock"),
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
            "price": forms.NumberInput(
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
class CategoryForm(forms.ModelForm):

    class Meta:

        model = Category

        fields = [
            "name",
            "color",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Category name")
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control category-color-input",
                    "type": "color",
                }
            ),

        }        
        
class ColorForm(forms.ModelForm):

    class Meta:

        model = Color

        fields = [
            "name",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Color name")
                }
            )

        }        
        
class InventoryTransactionForm(forms.ModelForm):

    class Meta:

        model = InventoryTransaction

        fields = [

            "product",

            "transaction_type",

            "quantity",

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
        
class SizeForm(forms.ModelForm):

    class Meta:

        model = Size

        fields = [
            "name",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Size name")
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
    password = forms.CharField(label='كلمة المرور', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='الاسم الأول', max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='الاسم العائلة', max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    perm_inventory = forms.BooleanField(label='إدارة المخزون (إضافة/تعديل المنتجات)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_sales = forms.BooleanField(label='إدارة المبيعات (حركات مخزنية)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_reports = forms.BooleanField(label='التقارير (رؤية الأرباح وتقارير الجرد)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_delete = forms.BooleanField(label='صلاحية الحذف (حذف المنتجات والحركات)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    password = forms.CharField(label='تغيير كلمة المرور (اتركه فارغاً للإبقاء عليها)', required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(label='نشط (يمكنه تسجيل الدخول)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    perm_inventory = forms.BooleanField(label='إدارة المخزون (إضافة/تعديل المنتجات)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_sales = forms.BooleanField(label='إدارة المبيعات (حركات مخزنية)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_reports = forms.BooleanField(label='التقارير (رؤية الأرباح وتقارير الجرد)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    perm_delete = forms.BooleanField(label='صلاحية الحذف (حذف المنتجات والحركات)', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_active')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
